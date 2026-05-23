VX300S — Push
=============

The arm must push a 4 cm cube across the cafe-table to a goal point
on the table top. The closed gripper acts as a flat paddle (gripper
not in the action vector). Achieved goal is the cube position.

Env IDs: ``VX300SPushSim-v0`` / ``VX300SPushGoalSim-v0`` /
``VX300SPushReal-v0`` / ``VX300SPushGoalReal-v0``.

Description
-----------

VX300S flush-mounted on the cafe-table (z = 0.78). At reset the arm
goes to home pose, the gripper closes
(``init_close_gripper = [0.025, -0.025]`` m), and a red cube spawns
on the table top at z = 0.795. The agent commands joint-space or
EE-space deltas; contact with the closed gripper slides the cube
toward the goal.

Action Space
------------

**Joint mode** (default). Box(6,) — same 6-joint command as
:doc:`reach` (waist / shoulder / elbow / forearm_roll / wrist_angle
/ wrist_rotate). Gripper is NOT in the action vector for push.

**EE mode** (``ee_action_type=True``). Box(3,) — Δ EE position.

Observation Space
-----------------

**Standard env (``VX300SPushSim-v0`` / ``VX300SPushReal-v0``).** Box.
Extends the reach obs with cube state:

.. list-table::
   :widths: 8 14 36 30 12
   :header-rows: 1

   * - Idx
     - Dim
     - Component
     - Source
     - Unit
   * - 0–2
     - 3
     - EE position
     - MoveIt FK
     - m
   * - 3–5
     - 3
     - EE rpy
     - MoveIt
     - rad
   * - 6–8
     - 3
     - Unit vector cube → goal
     - normalized
     - unitless
   * - 9
     - 1
     - Distance cube → goal
     - ‖goal − cube‖
     - m
   * - 10–18
     - 9
     - Current joint positions
     - ``/vx300s/joint_states``
     - rad / m
   * - 19–24
     - 6 (or 3)
     - Previous action
     - cached
     - matches action space
   * - 25–33
     - 9
     - Current joint velocities
     - ``/vx300s/joint_states``
     - rad/s / m/s
   * - 34–36
     - 3
     - Cube position (base frame)
     - Gazebo / ``/cube_pose``
     - m
   * - 37–39
     - 3
     - Cube rpy
     - same source
     - rad
   * - 40–42
     - 3
     - Cube linear velocity (finite-diff)
     - cached + dt
     - m/s
   * - 43–45
     - 3
     - Cube angular velocity
     - cached + dt
     - rad/s
   * - 46–48
     - 3
     - Cube relative to EE
     - cube − ee
     - m

**Goal env (``VX300SPushGoalSim-v0`` / ``VX300SPushGoalReal-v0``).** Dict.
``desired_goal`` = Box(3,) on table top (``x ∈ [0.20, 0.35]``,
``y ∈ [-0.15, 0.15]``, ``z ≈ 0.015`` from the on-table-base
perspective — the goal sampling is in the vx300s/base_link frame).
``achieved_goal`` = Box(3,) cube XYZ.

Rewards
-------

**Sparse**: ``0.0`` if ``‖cube − goal‖ < reach_tolerance`` else
``-1.0``.

**Dense**: same reward components as :doc:`reach` but distance is
measured from the **cube** to the goal (not EE to goal). Defaults
from ``config/vx300s_push_task_config.yaml`` match the reach
defaults plus push-specific reset / shaping.

Starting State
--------------

Joint pose: zeros (Interbotix URDF home; safe on-table mount).
Gripper closed at ``init_close_gripper = [0.025, -0.025]`` m.

**Cube spawn.** 4 cm red cube at default
``cube_init_pos = [0.25, 0.0, 0.015]`` in the base frame (=
``[0.45, 0.0, 0.795]`` in world). Randomised within
``random_cube_spawn`` box if enabled.

**Goal sampling.** Push goal ∈ Box(3,) on the table top within
``position_goal_min/max``. The ``goal_x_min`` was bumped from 0.15
to 0.20 — the VX300S's longer reach pushes the near-base
dead-zone further out than the RX200's.

Episode End
-----------

**Truncation.** ``max_episode_steps`` (default 100). Real env also
on stale ``/joint_states``.

**Termination.** ``‖cube − goal‖ < reach_tolerance`` (sparse only).

Arguments
---------

Inherits :doc:`reach` kwargs plus push-specific:
``random_cube_spawn`` (bool), ``random_goal`` (bool),
``cube_pose_topic`` *(real only, default ``/cube_pose``)*,
``cube_pose_timeout_s`` *(real only, default 1.0 s)*,
``auto_launch_cube_tracker`` / ``cube_tracker_camera`` /
``cube_tracker_target_frame`` *(real only)*.

Version History
---------------

* ``v0`` — first release (``rl_environments`` v0.1.0). Closed-gripper
  paddle. ``goal_x_min=0.20`` (bumped from 0.15 due to VX300S
  near-base dead-zone).
