Ecosystem overview
==================

The framework is intentionally split into four packages. Each
solves a clearly-bounded problem; users compose them depending on
whether they're training in simulation, on hardware, or both.

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

The framework tracks the roscores and Gazebo processes each script
spawns and tears them down on ``Ctrl+C`` or normal interpreter
exit. The mechanism is layered:

1. **Targeted signal handler.** ``register_managed_process`` (called
   internally by ``launch_roscore`` / ``launch_gazebo``) installs a
   SIGINT handler plus an ``atexit`` hook.
2. **rospy shutdown hook.** Because ``rospy.init_node`` installs
   its own SIGINT handler that would otherwise overwrite ours,
   ``register_managed_process`` also registers via
   ``rospy.on_shutdown``. This is what guarantees cleanup runs in
   the common ``launch_gazebo; rospy.init_node; train`` flow.
3. **Targeted ``pkill``.** Each tracked roscore is killed by its
   port (``pkill -f "roscore -p <port>"``), and Gazebo's
   gzserver / gzclient PIDs are captured at launch and SIGTERM'd
   individually. Pre-existing ROS sessions on the host are not
   affected.
4. **Escape hatch.** After cleanup runs, SIGINT is reset to
   ``SIG_DFL`` so a subsequent Ctrl+C kills the script immediately
   even if the training loop is stuck in a non-responsive C call.

If you want to clobber every ROS / Gazebo session on the machine
(across users / scripts), use the explicit host-wide helpers:
:func:`multiros.utils.ros_common.kill_all_host_ros_and_gazebo` or
:func:`realros.utils.ros_common.kill_all_host_ros_processes`. The
``host`` in the name is the warning.


Reading further
---------------

* :doc:`/api/uniros` — the canonical class and shared utilities.
* :doc:`/api/multiros` — Gazebo-side API.
* :doc:`/api/realros` — real-hardware-side API.
* :doc:`/api/sb3_ros_support` — algorithm wrappers.
* :doc:`testing` — how to run the regression test suites.
