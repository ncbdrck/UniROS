RX200 — Reach
=============

The arm must move its end-effector to a 3D target sampled in the
workspace above the cafe-table. No cube; gripper not commanded.

Env IDs: ``RX200ReacherSim-v0`` / ``RX200ReacherGoalSim-v0`` /
``RX200ReacherReal-v0`` / ``RX200ReacherGoalReal-v0``. Sim-only ZED 2
sensor variants: ``RX200Zed2ReacherSim-v0`` /
``RX200Zed2ReacherGoalSim-v0``.

Description
-----------

A Trossen ReactorX-200 5-DoF arm with two prismatic gripper fingers
sits flush on a ``cafe_table`` (top at z = 0.78). Reach ≈ 550 mm.
Joint-space or EE-space deltas, per-link FK safety, real-time or
MDP-pause step mode — same architecture as the other robots'
reach env (see :doc:`/envs/ur5e/reach`).

Action Space
------------

**Joint mode** (default). Box(5,):

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
     - wrist angle delta
     - -1.87
     - +2.23
     - ``wrist_angle``
     - rad
   * - 4
     - wrist rotate delta
     - -3.14
     - +3.14
     - ``wrist_rotate``
     - rad

When ``delta_action=True`` (default), scaled by ``delta_coeff = 0.05``
and added to the current joint position.

**EE mode** (``ee_action_type=True``). Box(3,) — Δ EE position in
the ``rx200/base_link`` frame.

Observation Space
-----------------

**Standard env.** Box layout:

* EE position (3, base frame, m)
* Unit vector EE → goal (3, normalised)
* Distance EE → goal (1, m)
* Current joint positions (8, ``/rx200/joint_states.position``,
  alphabetical: elbow, gripper continuous, left_finger, right_finger,
  shoulder, waist, wrist_angle, wrist_rotate)
* Previous action (5 or 3)
* Current joint velocities (8)

**Goal env.** Dict with three keys. ``desired_goal`` /
``achieved_goal`` = Box(3,):

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
     - 0.15
     - 0.35
   * - 1
     - 1
     - goal y
     - -0.15
     - 0.15
   * - 2
     - 1
     - goal z
     - 0.02
     - 0.30

(Goal coords are in the ``rx200/base_link`` frame; base is at world
z = 0.78.)

Rewards
-------

**Sparse**: ``0.0`` if ``‖ee − goal‖ < 0.05`` else ``-1.0``.

**Dense**: dist-shaped + reached-goal bonus + per-step penalty +
joint/none/goal-space penalties. Defaults from
``config/rx200_reach_task_config.yaml``: ``reach_tolerance=0.05``,
``multiplier_dist_reward=2.0``, ``reached_goal_reward=20``,
``step_reward=-0.5``, ``joint_limits_reward=-2.0``,
``none_exe_reward=-5.0``, ``not_within_goal_space_reward=-2.0``.

.. code-block:: python

   env = gym.make("RX200ReacherSim-v0", reward_type="Dense")
   env = gym.make("RX200ReacherGoalSim-v0", reward_type="Sparse")

Starting State
--------------

Initial joint pose: zeros (Interbotix URDF home — safe for the
on-table mount):

.. code-block:: text

   waist        = 0.0
   shoulder     = 0.0
   elbow        = 0.0
   wrist_angle  = 0.0
   wrist_rotate = 0.0

**Goal sampling.** ``desired_goal`` ∈ Box(3,) from
``position_goal_min/max``. Per-link FK rejects sampled goals that
can't be reached without dipping a link below
``table_z + safety_z_margin``.

Episode End
-----------

**Truncation.** ``max_episode_steps`` (default 100). Real env aborts
on stale ``/rx200/joint_states``.

**Termination.** ``‖ee − goal‖ < reach_tolerance`` (sparse only).

Arguments
---------

Same kwargs as :doc:`/envs/ur5e/reach`. Sim-only variants:
``use_kinect`` (default) for ``/head_mount_kinect2/*``;
``RX200Zed2*`` IDs use the ZED 2 stereo camera instead.

Version History
---------------

* ``v0`` — first release (``rl_environments`` v0.1.0). Framework
  reference robot — most-exercised env in the ecosystem benchmarks
  (Use Cases A–C in the UniROS paper).
