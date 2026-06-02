Known limitations
=================

This page is the place where the docs are honest. The framework
works for the use cases the paper evaluates and the cleanup work
has shored up correctness, but several limitations are worth
flagging up front rather than discovering at integration time.


Platform lifecycle
------------------

* **ROS Noetic reached end-of-life on 2025-05-31.** Ubuntu 20.04
  reached end of standard support on 31 May 2025 (Ubuntu Pro
  extends to 2030). No new upstream Noetic packages will be
  released; security updates only via Ubuntu Pro.
* **Gazebo Classic reached EOL in 2025.** Modern Gazebo (Harmonic,
  Ionic) and ROS 2 are the forward path. A future port of this
  framework to ROS 2 / modern Gazebo is mentioned in the paper as
  future work but is not implemented here.
* The framework's container / docker workflow is informal — we
  assume native Ubuntu 20.04 installs. If you're starting on a
  modern machine in 2026 onward, a fixed-snapshot VM or Docker
  image is the easiest reproducibility path.


Coverage of the example environments
------------------------------------

The pre-built env matrix covers four robots × three tasks × sim/real
× standard/goal variants (48 core IDs) plus extra Kinect/ZED2 sensor
variants for RX200 — 54 registered Gymnasium IDs in total. See
:doc:`/envs/index` for the full inventory.

Maturity varies across that matrix:

* **RX200 reach** (sim and real) is the most exercised path; it is
  the joint sim+real workflow used for the paper experiments and
  the only env validated end-to-end on physical hardware so far.
* **RX200 push / PnP**, **Ned2 reach / push / PnP**, **VX300S
  reach / push / PnP**, and **UR5e reach / push / PnP** sim envs
  are registered and have training/validation scripts. They have
  been exercised in Gazebo but not all of them have been published
  with trained policies.
* **Real envs** are registered for every robot/task above, but
  hardware bring-up beyond RX200 reach is still in progress.
  Treat the real registry as "implemented in code", not
  "validated on hardware".
* **UR5e real** specifically depends on a
  ``ur5e_description_extras/launch/ur5e_real.launch`` wrapper that
  is still pending — see the UR5e pages under :doc:`/envs/index`.
* Variants exist for joint-position vs end-effector action spaces
  and for vision-based observations (Kinect v2, ZED 2, RealSense
  D405), but per-variant training/evaluation has not been published.


Real-robot training
-------------------

* Training on physical hardware is real-world reinforcement
  learning: the agent will execute random-ish actions early on.
  The framework provides Ctrl+C cleanup of the *processes* it
  spawned but does not impose action-space safety bounds for you.
  Joint limits, collision checks, and a reachable e-stop are
  the user's responsibility — see :doc:`env_creation_real` for the
  safety checklist.
* The framework was developed and tested against an RX200 arm
  connected over USB. Other connection topologies (Ethernet,
  wireless) introduce additional latency that the framework does
  not specifically compensate for.
* The cleanup mechanism tears down the script-spawned roscore and
  Gazebo on Ctrl+C; it does **not** touch the real robot driver
  running in another terminal. That driver must be stopped
  manually.


Multi-task wrapper assumptions
------------------------------

* :class:`rl_training_validation.utils.multi_task_env.MultiTaskEnv`
  and :class:`~rl_training_validation.utils.multi_task_goal_env.MultiTaskGoalEnv`
  **pad** observations and actions to the maximum dimensionality
  across sub-envs. Padding doesn't make semantically incompatible
  envs compatible — the policy will still see "0.0" padding in
  the slots the sub-env doesn't use, which the agent may interpret
  as meaningful zeros. Best used when sub-envs have *similar*
  observation/action spaces (e.g. same robot, different tasks; or
  sim + real of the same robot).
* The HER reward-recompute path in :class:`MultiTaskGoalEnv`
  relies on ``info["task_id"]`` being preserved by the replay
  buffer. ``sb3_ros_support`` HER stores ``info`` correctly; other
  replay implementations may not.


CI and documentation
--------------------

* The continuous-integration suite (103 pytest tests across the
  four core packages) stubs the rospy ecosystem; it doesn't
  actually instantiate roscore / Gazebo / MoveIt. So CI green
  doesn't fully replace a manual smoke test against a live ROS
  workspace before merging anything that touches IPC, Gazebo
  lifecycle, or controller bring-up.
* The Sphinx API pages use ``autodoc_mock_imports`` to read
  docstrings without the heavy ROS / KDL / MoveIt / SB3
  dependencies. That means the rendered API reference is faithful
  to the docstrings but does not exercise any code path.
* The framework currently pins **gymnasium 0.29.1**. A 1.x port
  is feasible but not done — gymnasium 1.x removed the wrapper
  attribute passthrough that the multiprocessing proxy depends on,
  so a small proxy-side change would be needed.


Forward-compatibility
---------------------

* The four core packages' ``setup.py`` files import ``distutils``,
  which was removed from the Python 3.12 standard library. The
  CI matrix runs Python 3.8 and 3.10 only for this reason. A
  ``distutils → setuptools`` migration would unblock 3.12 (and
  later) but hasn't landed.
* The cleanup work introduced a runtime dependency from
  ``multiros`` and ``realros`` onto ``uniros`` (for the canonical
  ``GymProxy``). That's reflected in their ``package.xml``, but
  users with an older workspace where MultiROS / RealROS are
  pinned to pre-cleanup versions will need to update UniROS too.
