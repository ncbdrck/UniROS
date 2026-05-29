NED2 — Reach
============

The arm must move its end-effector to a 3D target sampled in the
workspace above the cafe-table. No cube; gripper not commanded.

Env IDs: ``NED2ReacherSim-v0`` / ``NED2ReacherGoalSim-v0`` /
``NED2ReacherReal-v0`` / ``NED2ReacherGoalReal-v0``.

Description
-----------

A Niryo Ned2 6-DoF arm with 2 prismatic mors fingers sits on the
same cafe-table the RX200 uses. URDF link names are bare (no
``ned2/`` prefix on the URDF, although Gazebo's link-state lookup
uses the model-qualified ``ned2/<link>`` form). MoveIt SRDF group
``arm`` chains ``base_link → tool_link``.

Action Space
------------

**Joint mode** (default). Box(6,):

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
     - joint_1 delta (shoulder rot)
     - -2.949
     - +2.949
     - ``joint_1``
     - rad
   * - 1
     - joint_2 delta (arm rot)
     - -1.833
     - +0.610
     - ``joint_2``
     - rad
   * - 2
     - joint_3 delta (elbow rot)
     - -1.340
     - +1.570
     - ``joint_3``
     - rad
   * - 3
     - joint_4 delta (forearm rot)
     - -2.090
     - +2.090
     - ``joint_4``
     - rad
   * - 4
     - joint_5 delta (wrist rot)
     - -1.920
     - +1.923
     - ``joint_5``
     - rad
   * - 5
     - joint_6 delta (hand rot)
     - -2.530
     - +2.530
     - ``joint_6``
     - rad

Joint-1 bounds tightened from URDF's ±3.000 to ±2.949 as a 0.05 rad
safety margin. ``delta_action=True`` (default) scales by
``delta_coeff = 0.05``.

**EE mode** (``ee_action_type=True``). Box(3,) — Δ EE position
relative to ``base_link``.

Observation Space
-----------------

**Standard env.** Box layout:

* EE position (3, base_link frame, m)
* Unit vector EE → goal (3, normalised)
* Distance EE → goal (1, m)
* Current joint positions (8 — alphabetical: joint_1, joint_2,
  joint_3, joint_4, joint_5, joint_6, mors_1, mors_2)
* Previous action (6 or 3)
* Current joint velocities (8)

**Goal env.** Dict with three keys.
``desired_goal`` / ``achieved_goal`` = Box(3,). The bounds below are
the declared *observation-space* bounds (mirror
``position_desired_goal_min/max`` in ``ned2_reach_task_config.yaml``);
the per-episode *sampling* support is the narrower
``position_goal_min/max`` (see Goal sampling below).

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
     - 0.40
   * - 1
     - 1
     - goal y
     - -0.40
     - 0.40
   * - 2
     - 1
     - goal z
     - 0.10
     - 0.40

Rewards
-------

**Sparse**: ``0.0`` if ``‖ee − goal‖ < 0.02`` else ``-1.0``.

**Dense**: same shape as the other robots' reach envs. Defaults
from ``config/ned2_reach_task_config.yaml``: ``reach_tolerance=0.02``,
``multiplier_dist_reward=2.0``, ``reached_goal_reward=20``,
``step_reward=-0.5``.

.. code-block:: python

   env = gym.make("NED2ReacherSim-v0", reward_type="Dense")
   env = gym.make("NED2ReacherGoalSim-v0", reward_type="Sparse")

Starting State
--------------

Initial joint pose: URDF zero
(``init_pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]`` — Niryo's "fully
extended forward and up" pose; consider switching to a Niryo-style
sleep pose like ``[0.0, 0.55, -1.5, 0.0, 0.0, 0.0]`` if your bench
lacks vertical clearance).

**Goal sampling.** ``desired_goal`` ∈ Box(3,) from
``position_goal_min/max``. Per-link FK safety enforces the
``table_z + safety_z_margin`` floor.

Episode End
-----------

**Truncation.** ``max_episode_steps`` (default 100). Real env aborts
on stale ``/ned2/joint_states``.

**Termination.** ``‖ee − goal‖ < reach_tolerance`` (sparse only).

Arguments
---------

Same kwargs as :doc:`/envs/ur5e/reach`, plus NED2-specific:

* ``use_wrist_camera`` (bool, default False) — subscribes to
  ``/gazebo_camera/image_raw`` (sim) or
  ``/niryo_robot_vision/compressed_video_stream`` (real) for
  Niryo's built-in tool camera. Decoded frame exposed as
  ``self.cv_image_wrist``.

Version History
---------------

* ``v0`` — first release (``rl_environments`` v0.1.0). Bare URDF
  link names. MoveIt SRDF group ``arm`` ends at ``tool_link``.
