NED2 — Pick-and-Place
=====================

The arm must grasp a 4 cm cube, lift it, and place it at a target
point. Action vector gains one extra scalar at ``action[-1]``
controlling the mors gripper. Optional ``multi_goal`` lift-then-place
curriculum.

Env IDs: ``NED2PnPSim-v0`` / ``NED2PnPGoalSim-v0`` /
``NED2PnPReal-v0`` / ``NED2PnPGoalReal-v0``.

Description
-----------

Niryo Ned2 6-DoF arm flush on the cafe-table. At reset the arm goes
to init pose, the gripper **opens**, and the cube spawns on the
table. ``is_grasped`` triggers when
``‖cube − ee‖ < grasp_dist_thresh`` AND
``mors_1_pos < grasp_finger_thresh``.

Action Space
------------

**Joint mode** (default). Box(7,):

* Indices 0–5: 6-joint arm command (same as :doc:`reach`).
* Index 6: gripper command (absolute ``mors_1`` position) ∈
  [-0.01, +0.01] m. On sim, the trajectory is published directly to
  ``gazebo_tool_commander`` with both mors mirrored. On real, the
  scalar is thresholded to a binary
  ``niryo_robot_tools_commander`` "open"/"close" action.

**EE mode** (``ee_action_type=True``). Box(4,) — Δ EE position +
gripper command.

Observation Space
-----------------

**Standard env.** Box. Extends push obs with ``is_grasped`` (1 dim,
0/1 float).

**Goal env.** Dict. ``desired_goal`` = Box(3,) with z up to lift
height. ``achieved_goal`` = cube XYZ.

Rewards
-------

**Sparse**: ``0.0`` if ``‖cube − pnp_goal‖ < reach_tolerance`` else
``-1.0``.

**Dense** with ``multi_goal=True`` and grasp shaping:

.. code-block:: text

   reward = -multiplier_dist_reward * ‖cube − current_goal‖
          + grasp_bonus if is_grasped
          + reached_goal_reward if ‖cube − pnp_goal‖ < reach_tolerance
          + step_reward + (joint/none/goal-space penalties)

Defaults from ``config/ned2_pnp_task_config.yaml``:
``grasp_dist_thresh=0.05``, ``grasp_finger_thresh = 0.0`` (m —
**placeholder; calibrate empirically before relying on
``is_grasped``**), ``lift_height=0.15``.

.. code-block:: python

   env = gym.make("NED2PnPSim-v0", reward_type="Dense", multi_goal=True)
   env = gym.make("NED2PnPGoalSim-v0", reward_type="Sparse", multi_goal=True)

Starting State
--------------

Joint pose: URDF zero. Gripper **open**
(``init_open_gripper = [0.01, 0.01]`` m).

**Cube spawn.** 4 cm red cube at default
``cube_init_pos = [0.25, 0.0, 0.015]`` in base frame. Note: sim env
has ``[0.180, 0.000, 0.015]`` hardcoded fallback —
**inconsistent with YAML**; align before relying on the static
spawn.

**Goal sampling.** ``pnp_goal`` ∈ Box(3,) from
``position_goal_min/max``. With ``multi_goal=True``,
``intermediate_goal = cube_init + [0, 0, 0.15]``.

Episode End
-----------

**Truncation.** ``max_episode_steps`` (default 100). Real env on
stale ``/ned2/joint_states``.

**Termination.** ``‖cube − pnp_goal‖ < reach_tolerance`` (sparse
only).

Arguments
---------

Inherits :doc:`reach` and :doc:`push` kwargs plus pnp-specific:

* ``multi_goal`` (bool, default True) — lift-then-place curriculum.
* ``lift_height`` (float, default 0.15 m) — vertical offset of
  ``intermediate_goal`` above cube spawn.
* ``use_wrist_camera`` (bool, default False) — opt-in Niryo wrist
  camera subscriber for close-up perception.

Version History
---------------

* ``v0`` — first release (``rl_environments`` v0.1.0).
  ``grasp_finger_thresh = 0.0`` is a placeholder — measure the
  closed mors position on the actual hardware and update the YAML
  before relying on ``is_grasped`` in real training.
