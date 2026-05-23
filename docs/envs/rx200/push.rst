RX200 — Push
============

The arm must push a 4 cm cube across the cafe-table to a goal point
on the table top. Closed gripper acts as a flat paddle.

Env IDs: ``RX200PushSim-v0`` / ``RX200PushGoalSim-v0`` /
``RX200PushReal-v0`` / ``RX200PushGoalReal-v0``. Sim-only ZED 2 variants:
``RX200Zed2PushSim-v0`` / ``RX200Zed2PushGoalSim-v0``.

Description
-----------

RX200 flush-mounted on the cafe-table. At reset the arm goes to
home pose, the gripper closes
(``init_close_gripper = [0.018, -0.018]`` m), and a red cube spawns
on the cafe-table top.

Action Space
------------

**Joint mode** (default). Box(5,) — same 5-joint command as
:doc:`reach` (waist / shoulder / elbow / wrist_angle / wrist_rotate).
Gripper is NOT in the action vector for push.

**EE mode** (``ee_action_type=True``). Box(3,) — Δ EE position.

Observation Space
-----------------

**Standard env.** Box. Extends the reach obs with cube state:

* EE position (3, m)
* EE rpy (3, rad)
* Unit vector cube → goal (3, normalised)
* Distance cube → goal (1, m)
* Current joint positions (8 — alphabetical: elbow, gripper,
  left_finger, right_finger, shoulder, waist, wrist_angle, wrist_rotate)
* Previous action (5 or 3)
* Current joint velocities (8)
* Cube position in base frame (3, m)
* Cube rpy (3, rad)
* Cube linear velocity (3, m/s, finite-difference)
* Cube angular velocity (3, rad/s, finite-difference)
* Cube position relative to EE (3, m)

**Goal env.** Dict. ``desired_goal`` = Box(3,) on table top
(``x ∈ [0.15, 0.35]``, ``y ∈ [-0.15, 0.15]``, ``z ≈ 0.015``).
``achieved_goal`` = Box(3,) cube XYZ.

Rewards
-------

**Sparse**: ``0.0`` if ``‖cube − goal‖ < reach_tolerance`` else ``-1.0``.

**Dense**: same shape as :doc:`reach`, but distance is from CUBE to
goal (not EE to goal). Defaults from
``config/rx200_push_task_config.yaml``.

Starting State
--------------

Joint pose: zeros (URDF home). Gripper closed at
``init_close_gripper = [0.018, -0.018]`` m.

**Cube spawn.** 4 cm red cube at default
``cube_init_pos = [0.25, 0.0, 0.015]`` in base frame. Randomised XY
if ``random_cube_spawn=True``.

**Goal sampling.** Push goal ∈ Box(3,) on the table top within
``position_goal_min/max``.

Episode End
-----------

**Truncation.** ``max_episode_steps`` (default 100). Real env on
stale ``/rx200/joint_states``.

**Termination.** ``‖cube − goal‖ < reach_tolerance`` (sparse only).

Arguments
---------

Inherits :doc:`reach` kwargs plus push-specific
``random_cube_spawn`` / ``random_goal`` / *(real only)*
``cube_pose_topic`` (default ``/cube_pose``), ``cube_pose_timeout_s``
(1.0 s), ``auto_launch_cube_tracker`` / ``cube_tracker_camera`` /
``cube_tracker_target_frame``.

Version History
---------------

* ``v0`` — first release (``rl_environments`` v0.1.0).
