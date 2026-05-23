UR5e — Push
===========

The arm must push a 4 cm cube across the cafe-table to a goal point
on the table top. The Robotiq gripper is held closed throughout (it
acts as a flat paddle); the gripper is not in the action vector.
Achieved goal is the cube position; desired goal is the sampled
target on the table top.

This page covers four registered Gymnasium env IDs:

* ``UR5ePushSim-v0`` — standard, Gazebo
* ``UR5ePushGoalSim-v0`` — goal-conditioned (HER), Gazebo
* ``UR5ePushReal-v0`` — standard, real hardware
* ``UR5ePushGoalReal-v0`` — goal-conditioned, real hardware

Description
-----------

Same hardware geometry as :doc:`reach` (UR5e on 4-legged ``ur5_base``
next to the cafe-table at world (0.7, 0)). At reset the arm folds
up, the gripper closes, and a red cube spawns on the cafe-table top
at z = 0.795. The agent commands joint-space (default) or EE-space
deltas; the closed gripper makes contact with the cube and the
cube slides toward the target. Episodes end when the cube reaches
the goal point (``‖cube − goal‖ < reach_tolerance``) or after the
truncation limit.

Per-link FK safety, joint-state staleness gate, ``--allow-real-robot-motion``
real-side gate — all identical to the reach env.

Action Space
------------

**Joint mode** (default, ``ee_action_type=False``). Box(6,) — same
6-joint arm command as :doc:`reach`. The gripper is NOT in the action
vector for push.

**EE mode** (``ee_action_type=True``). Box(3,) — Δ EE position. The
env solves IK and publishes the joint-space trajectory through the
same per-link FK safety check.

See :doc:`reach` for the per-joint Min/Max table (identical here).

Observation Space
-----------------

**Standard env (``UR5ePushSim-v0`` / ``UR5ePushReal-v0``).**
Box obs adds cube state on top of the arm state used by reach.
Full layout (default, joint-mode):

.. list-table::
   :widths: 8 16 36 28 12
   :header-rows: 1

   * - Idx
     - Dim
     - Component
     - Source
     - Unit
   * - 0–2
     - 3
     - EE position (base frame)
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
     - Euclidean distance cube → goal
     - ‖goal − cube‖
     - m
   * - 10–16
     - 7
     - Current joint positions
     - ``/ur5e/joint_states.position``
     - rad
   * - 17–22
     - 6 (or 3)
     - Previous action
     - cached
     - matches action space
   * - 23–29
     - 7
     - Current joint velocities
     - ``/ur5e/joint_states.velocity``
     - rad/s
   * - 30–32
     - 3
     - Cube position (base frame)
     - Gazebo ``get_model_state`` (sim) /
       ``/cube_pose`` (real)
     - m
   * - 33–35
     - 3
     - Cube rpy
     - same source
     - rad
   * - 36–38
     - 3
     - Cube linear velocity (finite-diff)
     - cached + dt
     - m/s
   * - 39–41
     - 3
     - Cube angular velocity (finite-diff)
     - cached + dt
     - rad/s
   * - 42–44
     - 3
     - Cube position relative to EE
     - cube_pos − ee_pos
     - m

**Goal env (``UR5ePushGoalSim-v0`` / ``UR5ePushGoalReal-v0``).**
Dict with three keys:

``observation`` — Box, same as standard env's Box minus the goal-related
columns (no goal info leaks into the policy's plain observation).

``desired_goal`` — Box(3,). Sampled XYZ target on the cafe-table top:

.. list-table::
   :widths: 8 16 32 22 22
   :header-rows: 1

   * - Idx
     - Dim
     - Component
     - Min
     - Max
   * - 0
     - 1
     - goal x
     - 0.40
     - 0.80
   * - 1
     - 1
     - goal y
     - -0.30
     - 0.30
   * - 2
     - 1
     - goal z
     - 0.785
     - 0.80

``achieved_goal`` — Box(3,). Current **cube** XYZ (not EE — push
tracks the cube). Same coordinate frame as ``desired_goal``.

Rewards
-------

**Sparse** (required for HER):

.. code-block:: text

   reward = 0.0  if ‖cube − goal‖ < reach_tolerance else -1.0

**Dense** (default for std env):

.. code-block:: text

   reward = -multiplier_dist_reward * ‖cube − goal‖
          + reached_goal_reward     if ‖cube − goal‖ < reach_tolerance
          + step_reward             every step
          + joint_limits_reward     if action outside joint bounds
          + none_exe_reward         if MoveIt plan / FK safety rejects
          + not_within_goal_space_reward  if goal sampling failed

Defaults (from ``config/ur5e_push_task_config.yaml``):
``reach_tolerance=0.05``, ``multiplier_dist_reward=2.0``,
``reached_goal_reward=20``, ``step_reward=-0.5``,
``joint_limits_reward=-2.0``, ``none_exe_reward=-5.0``,
``not_within_goal_space_reward=-2.0``.

Starting State
--------------

Same folded-upright joint pose as :doc:`reach`. After the joint
config is applied, the gripper is commanded closed
(``init_close_gripper = [0.7]`` rad knuckle).

**Cube spawn.** A 4 cm red cube spawns at world coordinates
``(0.500, -0.150, 0.795)`` by default. ``random_cube_spawn=True``
(default) randomises the XY within
``cube_init_pos ± random_offset``. The cube model is removed and
re-spawned at every reset to clear residual physics.

**Goal sampling.** ``desired_goal`` ∈ Box(3,) drawn from the
``position_goal_min/max`` rosparams above. Goals always sit on the
cafe-table top (z ≈ 0.795).

Episode End
-----------

**Truncation.** Episodes truncate after ``max_episode_steps`` (default
100). Real env additionally aborts the loop tick if
``/ur5e/joint_states`` is stale for > ``joint_state_timeout_s`` (0.5 s).

**Termination.** Episode terminates when
``‖cube − goal‖ < reach_tolerance`` (sparse reward path only — dense
keeps shaping past the goal until the time limit).

Arguments
---------

Inherits all kwargs from :doc:`reach` plus push-specific:

.. list-table::
   :widths: 24 14 62
   :header-rows: 1

   * - Kwarg
     - Default
     - Meaning
   * - ``random_cube_spawn``
     - ``True``
     - Randomise cube XY within the spawn box each reset.
   * - ``random_goal``
     - ``True``
     - Randomise the push goal each reset (else use the static
       ``push_goal`` from ``_set_init_params``).
   * - ``cube_pose_topic`` *(real only)*
     - ``/cube_pose``
     - Topic the env subscribes to for cube pose
       (``geometry_msgs/PoseStamped``).
   * - ``auto_launch_cube_tracker`` *(real only)*
     - ``False``
     - If ``True``, the env auto-launches
       ``rl_envs_cube_tracker/<camera>.launch`` (default kinect2).
   * - ``cube_tracker_camera`` *(real only)*
     - ``"kinect2"``
     - One of ``"kinect2"``, ``"zed2"``, ``"d405"``.
   * - ``cube_tracker_target_frame`` *(real only)*
     - ``""``
     - If non-empty, TF-transforms ``/cube_pose`` into this frame
       (e.g. ``"base_link"`` for UR5e).

Version History
---------------

* ``v0`` — first release (``rl_environments`` v0.1.0). Closed-gripper
  paddle (``init_close_gripper = [0.7]`` rad knuckle). Goal x_min =
  0.40 (UR5e near-base dead-zone shifts further out than the
  Interbotix robots' goal box).
