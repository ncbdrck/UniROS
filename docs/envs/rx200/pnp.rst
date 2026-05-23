RX200 — Pick-and-Place
======================

The arm must grasp a 4 cm cube, lift it, and place it at a target
point (possibly elevated). Action vector gains one extra scalar at
``action[-1]`` controlling the gripper (absolute left-finger
position). ``is_grasped`` derived from cube-EE proximity AND
left-finger position. Optional ``multi_goal`` lift-then-place
curriculum.

Env IDs: ``RX200PnPSim-v0`` / ``RX200PnPGoalSim-v0`` /
``RX200PnPReal-v0`` / ``RX200PnPGoalReal-v0``. Sim-only ZED 2 variants:
``RX200Zed2PnPSim-v0`` / ``RX200Zed2PnPGoalSim-v0``.

Description
-----------

RX200 flush-mounted on the cafe-table. At reset the arm goes to
home pose, the gripper **opens**
(``init_open_gripper = [0.036, -0.036]`` m — opposite of push's
closed reset), and the cube spawns on the table.
``is_grasped`` flips on when ``‖cube − ee‖ < grasp_dist_thresh``
AND ``left_finger_pos < grasp_finger_thresh``.

Action Space
------------

**Joint mode** (default). Box(6,):

* Indices 0–4: 5-joint arm command (same as :doc:`reach`).
* Index 5: gripper command (absolute ``left_finger`` position) ∈
  [0.015, 0.037] m. ``right_finger = -left_finger`` set just before
  publishing.

**EE mode** (``ee_action_type=True``). Box(4,) — Δ EE position +
gripper command.

Observation Space
-----------------

**Standard env.** Box. Extends push obs with ``is_grasped`` (1 dim,
binary 0/1).

**Goal env.** Dict. ``desired_goal`` = Box(3,); z range extends up
to 0.20 m above the table for place-at-height. ``achieved_goal`` =
cube XYZ.

Rewards
-------

**Sparse**: ``0.0`` if ``‖cube − pnp_goal‖ < reach_tolerance`` else
``-1.0``.

**Dense** with ``multi_goal=True``:

.. code-block:: text

   reward = -multiplier_dist_reward * ‖cube − current_goal‖
          + grasp_bonus  if is_grasped
          + reached_goal_reward  if ‖cube − pnp_goal‖ < reach_tolerance
          + step_reward
          + (joint/none/goal-space penalties)

``current_goal`` is the intermediate lift target
(``cube_init + [0, 0, lift_height=0.15]``) until reached, then
``pnp_goal``.

Defaults: ``grasp_dist_thresh=0.05``, ``grasp_finger_thresh=0.020``,
``lift_height=0.15``.

.. code-block:: python

   env = gym.make("RX200PnPSim-v0", reward_type="Dense", multi_goal=True)
   env = gym.make("RX200PnPGoalSim-v0", reward_type="Sparse", multi_goal=True)

Starting State
--------------

Joint pose: zeros (URDF home). Gripper **open** at
``init_open_gripper = [0.036, -0.036]`` m.

**Cube spawn.** 4 cm red cube at default
``[0.25, 0.0, 0.015]`` in base frame.

**Goal sampling.** ``pnp_goal`` ∈ Box(3,) from ``position_goal_min/max``.
With ``multi_goal=True``,
``intermediate_goal = cube_init + [0, 0, 0.15]``.

Episode End
-----------

**Truncation.** ``max_episode_steps`` (default 100). Real env on
stale ``/rx200/joint_states``.

**Termination.** ``‖cube − pnp_goal‖ < reach_tolerance`` (sparse
only).

Arguments
---------

Inherits :doc:`reach` and :doc:`push` kwargs plus pnp-specific:

* ``multi_goal`` (bool, default True) — lift-then-place curriculum.
* ``lift_height`` (float, default 0.15 m) — vertical offset of
  ``intermediate_goal`` above cube spawn.

Version History
---------------

* ``v0`` — first release (``rl_environments`` v0.1.0). Grasp
  comparison: ``left_finger_pos < grasp_finger_thresh`` (prismatic
  finger convention).
