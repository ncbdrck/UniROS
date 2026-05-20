Ecosystem overview
==================

The **core framework** is intentionally split into four packages
— UniROS, MultiROS, RealROS, and ``sb3_ros_support``. Each solves
a clearly-bounded problem; users compose them depending on
whether they're training in simulation, on hardware, or both.

Two additional **application** packages ship pre-built envs and
working training scripts on top: ``rl_environments`` (the gym envs
themselves) and ``rl_training_validation`` (the training scripts
that exercise them). They're optional — the framework runs without
them — but they're the easiest path to a first running example.

Architecture at a glance
------------------------

.. code-block:: text

      +---------------------------+      +---------------------------+
      |        multiros           |      |         realros           |
      |  Gazebo simulation envs   |      |  Real-hardware envs       |
      |  - launch_gazebo          |      |  - direct controller I/O  |
      |  - parallel roscores      |      |  - MoveIt integration     |
      |  - physics tuning         |      |                           |
      +-------------+-------------+      +-------------+-------------+
                    |                                  |
                    |  both re-export from             |
                    v                                  v
              +------------------------------------------+
              |                  UniROS                  |
              |   uniros._proxy.GymProxy  (canonical)    |
              |   uniros.utils.{ros_markers,             |
              |                 ros_kinematics,          |
              |                 ros_controllers}         |
              |   uniros.utils.ros_common               |
              |     - port allocator                    |
              |     - managed-process registry          |
              |     - on-Ctrl+C cleanup                 |
              +------------------------------------------+
                              ^
                              | trained by
                              |
              +------------------------------------------+
              |             sb3_ros_support              |
              |  Stable Baselines 3 algorithm wrappers   |
              |  PPO  A2C  DDPG  TD3  SAC  DQN           |
              |  + goal-conditioned variants (HER)       |
              +------------------------------------------+


Why four packages?
------------------

**UniROS** is the abstraction layer. It hosts the multiprocessing
gym-env proxy class (:class:`uniros._proxy.GymProxy`) and the ROS
utility modules shared by every package. multiros and realros
re-export the proxy under their historical names (``MultirosGym``,
``RealrosGym``) so existing code keeps working; new code can import
``uniros.GymProxy`` directly.

**multiros** focuses on Gazebo: launching simulators on arbitrary
ports, spawning multiple parallel envs against the same rosmaster,
tuning physics parameters per env. It depends on UniROS for the
shared utilities and the proxy class.

**realros** is the real-world counterpart. Same gym API, but talks
to physical robot drivers and (optionally) MoveIt instead of
Gazebo. Code written against ``multiros.make()`` can in many cases
be swapped to ``realros.make()`` with only configuration changes.

**sb3_ros_support** adapts Stable Baselines 3 to ROS-based training
scripts. Each algorithm subclass exposes the same training /
validation / save / load surface so swapping PPO for SAC for TD3
is a YAML edit, not a code rewrite.


Multiprocessing model
---------------------

Every gym env created via ``multiros.make()`` / ``realros.make()``
runs inside a worker ``multiprocessing.Process``. The parent holds
a :class:`uniros._proxy.GymProxy` instance that forwards
``step`` / ``reset`` / ``close`` / attribute access over a
``multiprocessing.Pipe`` to the worker.

This buys two important properties:

1. **Isolated rospy state per env.** Each worker has its own
   ``rospy.init_node`` and its own callbacks; envs can run in
   parallel against different rosmasters without bleeding
   subscriptions into each other.
2. **Crash isolation.** A misbehaving worker raises a Python
   exception, which the framework catches and ships back to the
   parent as a :class:`uniros._proxy._RemoteException`. The parent
   re-raises with the worker's traceback instead of hanging on the
   next ``recv()``.


Lifecycle / cleanup
-------------------

The framework tracks the roscores, Gazebo processes, and roslaunch /
rosrun xterms each script spawns and tears them down on ``Ctrl+C`` or
normal interpreter exit. The mechanism is layered:

1. **Targeted signal handler.** ``register_managed_process`` (called
   internally by ``launch_roscore`` / ``launch_gazebo`` /
   ``ros_launch_launcher`` / ``ros_node_launcher``) installs a
   SIGINT handler plus an ``atexit`` hook.
2. **rospy shutdown hook.** Because ``rospy.init_node`` installs
   its own SIGINT handler that would otherwise overwrite ours,
   ``register_managed_process`` also registers via
   ``rospy.on_shutdown``. This is what guarantees cleanup runs in
   the common ``launch_gazebo; rospy.init_node; train`` flow.
3. **Targeted ``pkill`` + process-group kill.** Each tracked
   roscore is killed by its port (``pkill -f "roscore -p <port>"``),
   and Gazebo's gzserver / gzclient PIDs are captured at launch and
   SIGTERM'd individually. Pre-existing ROS sessions on the host
   are not affected. As of v0.3.1, xterm wrappers from
   ``ros_launch_launcher`` and ``ros_node_launcher`` are also
   spawned as process-group leaders (``start_new_session=True``),
   and cleanup auto-detects session leaders and uses
   ``os.killpg(pgid, SIGTERM)`` to tear down the whole subtree
   (e.g. ``xterm → roslaunch → move_group →
   moveit_python_interface``) in one signal. Previously, terminating
   only the xterm left grandchildren orphaned to init.
4. **Escape hatch.** After cleanup runs, SIGINT is reset to
   ``SIG_DFL`` so a subsequent Ctrl+C kills the script immediately
   even if the training loop is stuck in a non-responsive C call.

Reliable launch verification (v0.3.1)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``launch_roscore`` verifies the spawned roscore is reachable (TCP
probe to the picked port) before returning. On failure, it retries
with a fresh kernel-allocated port up to three times, then raises
``RuntimeError``. Previously, a silent xterm/roscore failure (port
collision, stale process, display issue) would still report
"Roscore launched!" and set ``ROS_MASTER_URI`` at a phantom master.
Downstream ``wait_for_service`` calls then blocked their full 30 s
timeout, and ``roslaunch`` inside any subsequent ``launch_gazebo``
xterm would start its own rosmaster on an auto-allocated port — so
gzserver registered there and the env never found the ``/gazebo/*``
services it expected.

If you want to clobber every ROS / Gazebo session on the machine
(across users / scripts), use the explicit host-wide helpers:
:func:`multiros.utils.ros_common.kill_all_host_ros_and_gazebo` or
:func:`realros.utils.ros_common.kill_all_host_ros_processes`. The
``host`` in the name is the warning.


Three supported use cases
-------------------------

The UniROS paper (`Kapukotuwa et al., 2025
<https://www.mdpi.com/1424-8220/25/18/5679>`_, Section IX) lays
out three workflows the framework is designed to support. The
choice depends on whether you have a simulator, real hardware, or
both — and whether you want a sim-trained policy, a real-trained
policy, or a generalised policy that performs in both worlds:

.. list-table::
   :widths: 22 78
   :header-rows: 1

   * - Use case
     - What it looks like
   * - **Real-world only**
     - Train directly on the physical robot via RealROS. Every
       episode is a real episode. Slowest, but no reality-gap.
       See :doc:`env_creation_real` and :doc:`training`.
   * - **Sim → real transfer**
     - Train under a MultiROS env, save the model, validate on
       the matching RealROS env with no further updates.
       Reasonable when the simulator is close to reality.
       See :doc:`using_trained_models`.
   * - **Joint sim + real training**
     - Hold a sim env and a real env open at the same time,
       sample episodes from both, and update one policy from the
       combined replay buffer. The result is a single policy
       that's competent in both domains by construction.
       See :doc:`joint_sim_real_training`.


Framework-agnostic policies
---------------------------

The envs this framework produces are **standard gymnasium
environments**. Any reinforcement-learning library that accepts a
``gym.Env`` works: Stable Baselines 3, CleanRL, Tianshou, RLlib,
Tensorforce, or your own training loop. ``uniros.make()`` returns
a proxy that behaves like ``gym.Env`` while running the underlying
env in a worker process; the downstream training code is
unchanged.

:doc:`/api/sb3_ros_support` is a convenience layer for SB3 users
(YAML hyperparameter loading, ROS-aware paths, HER ready for goal
envs). It is **one option** — not a requirement.


Reading further
---------------

* :doc:`/api/uniros` — the canonical class and shared utilities.
* :doc:`/api/multiros` — Gazebo-side API.
* :doc:`/api/realros` — real-hardware-side API.
* :doc:`/api/sb3_ros_support` — algorithm wrappers (one option for
  SB3 users; vanilla SB3 / CleanRL / Tianshou / RLlib all work).
* :doc:`testing` — how to run the regression test suites.
