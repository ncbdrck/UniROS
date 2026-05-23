NED2 — Push
===========

The arm must push a 4 cm cube across the cafe-table to a goal point.
Closed gripper acts as a flat paddle (no gripper command in action).

Env IDs: ``NED2PushSim-v0`` / ``NED2PushGoalSim-v0`` /
``NED2PushReal-v0`` / ``NED2PushGoalReal-v0``.

Description
-----------

NED2 6-DoF arm flush on the cafe-table. At reset the arm goes to
init pose, the gripper closes (binary ``"close"`` command on real
via ``niryo_robot_tools_commander``; direct prismatic-mors
trajectory on sim), and a red cube spawns on the table top.

Action Space
------------

**Joint mode** (default). Box(6,) — same 6-joint command as
:doc:`reach` (joint_1 .. joint_6). Gripper NOT in action vector.

**EE mode** (``ee_action_type=True``). Box(3,) — Δ EE position.

Observation Space
-----------------

**Standard env.** Box. Extends reach obs with cube state:

* EE position (3, m)
* EE rpy (3, rad)
* Unit vector cube → goal (3, normalised)
* Distance cube → goal (1, m)
* Current joint positions (8, alphabetical)
* Previous action (6 or 3)
* Current joint velocities (8)
* Cube position in base frame (3, m)
* Cube rpy (3, rad)
* Cube linear velocity (3, m/s, finite-difference)
* Cube angular velocity (3, rad/s, finite-difference)
* Cube position relative to EE (3, m)

**Goal env.** Dict. ``desired_goal`` = Box(3,) on table top.
``achieved_goal`` = Box(3,) cube XYZ.

Rewards
-------

**Sparse**: ``0.0`` if ``‖cube − goal‖ < reach_tolerance`` else
``-1.0``.

**Dense**: dist-shaped on **cube** → goal, plus reached-goal bonus
and standard step / joint / none / goal-space penalties. Defaults
from ``config/ned2_push_task_config.yaml``.

Starting State
--------------

Joint pose: URDF zero (see :doc:`reach`). Gripper: closed (binary
``close`` on real; ``init_close_gripper = [-0.01, -0.01]`` m on
sim — mors prismatic limits are ±0.01 m).

**Cube spawn.** 4 cm red cube; default
``cube_init_pos = [0.25, 0.0, 0.015]`` in base frame. Sim env's
default hard-coded spawn is ``[0.180, 0.000, 0.015]`` —
**inconsistent with YAML**; tune ``random_cube_spawn=True`` or edit
``ned2_push_sim.py`` to align.

**Goal sampling.** Push goal ∈ Box(3,) on table top.

Episode End
-----------

**Truncation.** ``max_episode_steps`` (default 100); real env on
stale ``/ned2/joint_states``.

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

* ``v0`` — first release (``rl_environments`` v0.1.0). Gripper
  command is binary open/close on real (via
  ``niryo_robot_tools_commander``) and prismatic-trajectory on sim
  (via ``/gazebo_tool_commander/follow_joint_trajectory``).
