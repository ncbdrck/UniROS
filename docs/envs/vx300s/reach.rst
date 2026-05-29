VX300S — Reach
==============

The arm must move its end-effector to a 3D target sampled in the
workspace above the cafe-table. No cube; gripper not commanded.

This page covers four registered Gymnasium env IDs:

* ``VX300SReacherSim-v0`` — standard, Gazebo
* ``VX300SReacherGoalSim-v0`` — goal-conditioned (HER), Gazebo
* ``VX300SReacherReal-v0`` — standard, real hardware
* ``VX300SReacherGoalReal-v0`` — goal-conditioned, real hardware

Description
-----------

A ViperX-300 S 6-DoF arm with the standard Interbotix two-prismatic-
finger gripper sits flush on a ``cafe_table`` (top at z = 0.78). The
agent commands joint-space deltas (default) or absolute joint
positions, or alternatively EE-space deltas
(``ee_action_type=True``). Every commanded action passes through the
per-link FK safety check before being published.

The env loop runs at ``environment_loop_rate`` (default 10 Hz). In
real-time mode (``realtime_mode=True``, default), Gazebo physics is
never paused and ``step()`` reads the latest cached obs.

Action Space
------------

**Joint mode** (default, ``ee_action_type=False``). Box(6,):

.. list-table::
   :widths: 6 28 12 12 26 16
   :header-rows: 1

   * - Num
     - Action
     - Min
     - Max
     - Joint
     - Unit
   * - 0
     - waist delta
     - -3.14
     - +3.14
     - ``waist``
     - rad
   * - 1
     - shoulder delta
     - -1.85
     - +1.26
     - ``shoulder``
     - rad
   * - 2
     - elbow delta
     - -1.76
     - +1.61
     - ``elbow``
     - rad
   * - 3
     - forearm roll delta
     - -3.14
     - +3.14
     - ``forearm_roll``
     - rad
   * - 4
     - wrist angle delta
     - -1.87
     - +2.23
     - ``wrist_angle``
     - rad
   * - 5
     - wrist rotate delta
     - -3.14
     - +3.14
     - ``wrist_rotate``
     - rad

When ``delta_action=True`` (default), the action is scaled by
``delta_coeff = 0.05`` and added to the current joint position.

**EE mode** (``ee_action_type=True``). Box(3,) — Δ EE position in
the robot's base frame, x ∈ [-0.85, 0.85], y ∈ [-0.85, 0.85],
z ∈ [-0.85, 0.85] (loose obs bounds; actual table floor enforced
by ``workspace_min.z + safety_z_margin``).

Observation Space
-----------------

**Standard env (``VX300SReacherSim-v0`` / ``VX300SReacherReal-v0``).**
Box layout:

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
     - EE position (vx300s/base_link frame)
     - MoveIt FK
     - m
   * - 3–5
     - 3
     - Unit vector EE → goal
     - normalized
     - unitless
   * - 6
     - 1
     - Euclidean distance EE → goal
     - ‖goal − ee‖
     - m
   * - 7–15
     - 9
     - Current joint positions
     - ``/vx300s/joint_states.position``
     - rad / m
   * - 16–21
     - 6 (or 3)
     - Previous action
     - cached
     - matches action space
   * - 22–30
     - 9
     - Current joint velocities
     - ``/vx300s/joint_states.velocity``
     - rad/s / m/s

The 9-element joint vectors are in ``/joint_states`` order
(alphabetical): elbow, forearm_roll, gripper (continuous virtual
joint), left_finger, right_finger, shoulder, waist, wrist_angle,
wrist_rotate.

**Goal env (``VX300SReacherGoalSim-v0`` / ``VX300SReacherGoalReal-v0``).**
Dict with three keys. ``observation`` is the standard Box minus the
goal-related columns. ``desired_goal`` and ``achieved_goal`` are
Box(3,):

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
     - 0.25
     - 0.50
   * - 1
     - 1
     - goal y
     - -0.30
     - 0.30
   * - 2
     - 1
     - goal z
     - 0.20
     - 0.50

(Goal coordinates are in the ``vx300s/base_link`` frame which is at
world z = 0.78 — so a goal z of 0.20 is 1.0 m above the floor.)

Rewards
-------

**Sparse** (required for HER): ``0.0`` if ``‖ee − goal‖ < 0.02`` else
``-1.0``.

**Dense** (default for std env): dist-shaped penalty + reached-goal
bonus + per-step penalty + joint-limit / non-executable / not-in-goal-
space penalties. Defaults from ``config/vx300s_reach_task_config.yaml``:
``reach_tolerance=0.02``, ``multiplier_dist_reward=2.0``,
``reached_goal_reward=20``, ``step_reward=-0.5``,
``joint_limits_reward=-2.0``, ``none_exe_reward=-5.0``,
``not_within_goal_space_reward=-2.0``.

.. code-block:: python

   env = gym.make("VX300SReacherSim-v0", reward_type="Dense")
   env = gym.make("VX300SReacherGoalSim-v0", reward_type="Sparse")

Starting State
--------------

Initial joint pose (set via MoveIt
``set_trajectory_joints(init_pos)`` — the Interbotix URDF zero pose
is collision-free for the on-table mount):

.. code-block:: text

   waist        =  0.0
   shoulder     =  0.0
   elbow        =  0.0
   forearm_roll =  0.0
   wrist_angle  =  0.0
   wrist_rotate =  0.0

**Goal sampling.** ``desired_goal`` ∈ Box(3,) drawn from the
``position_goal_min/max`` rosparams (see table above). The
per-link FK safety check rejects sampled goals that aren't reachable
without dipping the wrist below ``table_z + safety_z_margin``.

Episode End
-----------

**Truncation.** ``max_episode_steps`` (default 100). Real env also
aborts on stale ``/joint_states`` (>
``joint_state_timeout_s = 0.5 s``).

**Termination.** ``‖ee − goal‖ < reach_tolerance`` (sparse only).

Arguments
---------

Same kwargs as :doc:`/envs/ur5e/reach` (``seed``, ``gazebo_gui``,
``reward_type``, ``ee_action_type``, ``delta_action``, ``delta_coeff``,
``environment_loop_rate``, ``action_cycle_time``, ``action_speed``,
``realtime_mode``, ``use_kinect``, ``log_internal_state``).

Real-only kwargs: inherits the ``--allow-real-robot-motion`` gate from
``rl_training_validation.utils.env_safety``.

Version History
---------------

* ``v0`` — first release (``rl_environments`` v0.1.0).
