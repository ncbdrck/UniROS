VX300S — Pick-and-Place
=======================

The arm must grasp a 4 cm cube, lift it, and place it at a target
point (possibly elevated above the table for place-at-height). The
action vector gains one extra scalar at ``action[-1]`` controlling
the gripper (absolute left-finger position). ``is_grasped`` is
derived from cube-EE proximity AND left-finger position; an optional
``multi_goal`` curriculum splits reward into lift target then place
target.

Env IDs: ``VX300SPnPSim-v0`` / ``VX300SPnPGoalSim-v0`` /
``VX300SPnPReal-v0`` / ``VX300SPnPGoalReal-v0``.

Description
-----------

Same VX300S hardware setup as :doc:`reach`. At reset the arm goes
to home pose, the gripper **opens**
(``init_open_gripper = [0.055, -0.055]`` m — opposite of push's
closed-gripper reset), and the cube spawns on the cafe-table.
``is_grasped`` flips on when:
``‖cube − ee‖ < grasp_dist_thresh`` (0.05 m) AND
``left_finger_pos < grasp_finger_thresh`` (0.024 m).

Action Space
------------

**Joint mode** (default). Box(7,):

* Indices 0–5: same as :doc:`reach`
  (waist, shoulder, elbow, forearm_roll, wrist_angle, wrist_rotate).
* Index 6: gripper command (absolute ``left_finger`` position) ∈
  [0.021, 0.057] m. ``right_finger`` is set to ``-left_finger`` just
  before publishing.

Gripper scalar is ALWAYS absolute regardless of ``delta_action``
(matches FetchPickAndPlace's gripper convention).

**EE mode** (``ee_action_type=True``). Box(4,) — Δ EE position +
gripper command.

Observation Space
-----------------

**Standard env.** Box. Extends the push obs with ``is_grasped``:

* All push obs components (EE pos+rpy, vec/dist to goal, joint pos,
  prev action, joint vel, cube pos+rpy+vel, cube_rel_to_ee).
* ``is_grasped`` (1 dim, float, 0.0 or 1.0).

The "current goal" in vec/dist columns is ``intermediate_goal`` (lift
target = cube_init + [0, 0, lift_height=0.15 m]) when
``multi_goal=True`` and the lift hasn't been reached yet, otherwise
``pnp_goal``.

**Goal env.** Dict. ``desired_goal`` = Box(3,) sampled XYZ; unlike
push the z range can extend up to 0.25 m above the table for
place-at-height. ``achieved_goal`` = Box(3,) cube XYZ.

Rewards
-------

**Sparse**: ``0.0`` if ``‖cube − pnp_goal‖ < reach_tolerance`` else
``-1.0``.

**Dense** with ``multi_goal=True`` and grasp-aware shaping:

.. code-block:: text

   reward = -multiplier_dist_reward * ‖cube − current_goal‖
          + grasp_bonus  if is_grasped
          + reached_goal_reward  if ‖cube − pnp_goal‖ < reach_tolerance
          + step_reward
          + (joint/none/goal-space penalties)

Defaults from ``config/vx300s_pnp_task_config.yaml``:
``grasp_dist_thresh=0.05``, ``grasp_finger_thresh=0.024``,
``lift_height=0.15``.

.. code-block:: python

   env = gym.make("VX300SPnPSim-v0", reward_type="Dense", multi_goal=True)
   env = gym.make("VX300SPnPGoalSim-v0", reward_type="Sparse", multi_goal=True)

Starting State
--------------

Joint pose: zeros (URDF home). Gripper **open** at
``init_open_gripper = [0.055, -0.055]`` m.

**Cube spawn.** 4 cm red cube at default
``cube_init_pos = [0.25, 0.0, 0.015]`` in base frame.

**Goal sampling.** ``pnp_goal`` ∈ Box(3,) from
``position_goal_min/max``. With ``multi_goal=True``,
``intermediate_goal = cube_init + [0, 0, 0.15]``.

Episode End
-----------

**Truncation.** ``max_episode_steps`` (default 100); real env also
on stale ``/joint_states``.

**Termination.** ``‖cube − pnp_goal‖ < reach_tolerance`` (sparse only).

Arguments
---------

Inherits :doc:`reach` and :doc:`push` kwargs plus pnp-specific:

.. list-table::
   :widths: 24 14 62
   :header-rows: 1

   * - Kwarg
     - Default
     - Meaning
   * - ``multi_goal``
     - ``True``
     - Lift-then-place curriculum.
   * - ``lift_height``
     - ``0.15`` m
     - Vertical offset of ``intermediate_goal`` above cube spawn.

Version History
---------------

* ``v0`` — first release (``rl_environments`` v0.1.0). Grasp
  comparison: ``left_finger_pos < grasp_finger_thresh`` (prismatic
  finger convention; opposite of UR5e's inverted knuckle comparison).
