UR5e — Pick-and-Place
=====================

The arm must grasp a 4 cm cube sitting on the cafe-table, lift it,
and place it at a target point — optionally elevated above the
table (place-at-height). The action vector gains one extra scalar
at ``action[-1]`` controlling the Robotiq knuckle. An ``is_grasped``
flag is derived from cube-EE proximity AND knuckle position; an
optional ``multi_goal`` curriculum splits the reward signal into a
lift target first, then the final place target.

This page covers four registered Gymnasium env IDs:

* ``UR5ePnPSim-v0`` — standard, Gazebo
* ``UR5ePnPGoalSim-v0`` — goal-conditioned (HER), Gazebo
* ``UR5ePnPReal-v0`` — standard, real hardware
* ``UR5ePnPGoalReal-v0`` — goal-conditioned, real hardware

Description
-----------

Hardware setup identical to :doc:`reach` (UR5e on ``ur5_base``,
cafe-table at x = 0.7). At reset the arm folds up, the gripper opens
(``init_open_gripper = [0.0]`` rad — *opposite* of push's closed
gripper), and the cube spawns on the cafe-table top. The agent
commands the 6-DoF arm plus the gripper scalar; ``is_grasped`` flips
on once the cube is within ``grasp_dist_thresh = 0.05 m`` of the EE
AND the knuckle has closed past ``grasp_finger_thresh ≈ 0.30 rad``.

Robotiq 2F-85 INVERTS the grasp comparison versus the
prismatic-finger robots (RX200, VX300S, NED2): the knuckle
position GROWS as the gripper closes (range 0.0 open → 0.8 closed).
The env reads ``gripper_open_value`` and ``gripper_closed_value``
rosparams so the reward + obs code doesn't have to know which way
the bounds map.

Action Space
------------

**Joint mode** (default, ``ee_action_type=False``). Box(7,):

.. list-table::
   :widths: 6 32 12 12 26 12
   :header-rows: 1

   * - Num
     - Action
     - Min
     - Max
     - Joint
     - Unit
   * - 0
     - shoulder pan delta
     - -3.14
     - +3.14
     - ``shoulder_pan_joint``
     - rad
   * - 1
     - shoulder lift delta
     - -3.14
     - +3.14
     - ``shoulder_lift_joint``
     - rad
   * - 2
     - elbow delta
     - -3.14
     - +3.14
     - ``elbow_joint``
     - rad
   * - 3
     - wrist 1 delta
     - -3.14
     - +3.14
     - ``wrist_1_joint``
     - rad
   * - 4
     - wrist 2 delta
     - -3.14
     - +3.14
     - ``wrist_2_joint``
     - rad
   * - 5
     - wrist 3 delta
     - -3.14
     - +3.14
     - ``wrist_3_joint``
     - rad
   * - 6
     - gripper command (absolute)
     - 0.0
     - 0.8
     - ``robotiq_85_left_knuckle_joint``
     - rad

The gripper scalar is ALWAYS treated as an absolute knuckle
position (regardless of ``delta_action``) — open/close is closer
to a discrete decision than a small delta; matches FetchPickAndPlace's
gripper convention. A single value is published; the other 5 finger
joints follow via the URDF mimic linkage.

**EE mode** (``ee_action_type=True``). Box(4,) — Δ EE position
(3 dims) + gripper command (1 dim).

Observation Space
-----------------

**Standard env (``UR5ePnPSim-v0`` / ``UR5ePnPReal-v0``).** Box. Layout
extends the push obs with grasp state:

.. list-table::
   :widths: 8 14 38 28 12
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
     - Unit vector cube → current goal
     - normalized
     - unitless
   * - 9
     - 1
     - Euclidean distance cube → current goal
     - ‖goal − cube‖
     - m
   * - 10–16
     - 7
     - Current joint positions
     - ``/ur5e/joint_states.position``
     - rad
   * - 17–23
     - 7 (or 4)
     - Previous action
     - cached
     - matches action space (incl. gripper scalar)
   * - 24–30
     - 7
     - Current joint velocities
     - ``/joint_states.velocity``
     - rad/s
   * - 31–33
     - 3
     - Cube position
     - Gazebo (sim) / ``/cube_pose`` (real)
     - m
   * - 34–36
     - 3
     - Cube rpy
     - same source
     - rad
   * - 37–39
     - 3
     - Cube linear velocity (finite-diff)
     - cached + dt
     - m/s
   * - 40–42
     - 3
     - Cube angular velocity (finite-diff)
     - cached + dt
     - rad/s
   * - 43–45
     - 3
     - Cube position relative to EE
     - cube_pos − ee_pos
     - m
   * - 46
     - 1
     - ``is_grasped`` (derived binary)
     - cube_rel_to_ee + knuckle pos
     - 0.0 or 1.0

The "current goal" in row 6–9 is ``intermediate_goal`` (lift target)
when ``multi_goal=True`` and the lift hasn't been reached yet;
otherwise it's the final ``pnp_goal``.

**Goal env (``UR5ePnPGoalSim-v0`` / ``UR5ePnPGoalReal-v0``).** Dict
with three keys:

``observation`` — Box, same as standard env's Box minus goal columns.

``desired_goal`` — Box(3,). Sampled XYZ target. Unlike push, can be
elevated off the table for place-at-height:

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
     - 0.795
     - 0.95

``achieved_goal`` — Box(3,). Current cube XYZ.

Rewards
-------

**Sparse** (required for HER):

.. code-block:: text

   reward = 0.0  if ‖cube − goal‖ < reach_tolerance else -1.0

**Dense** with ``multi_goal=True`` and grasp-aware shaping
(default for std env):

.. code-block:: text

   reward = -multiplier_dist_reward * ‖cube − current_goal‖
          + (grasp_bonus           if is_grasped else 0)
          + reached_goal_reward    if ‖cube − pnp_goal‖ < reach_tolerance
          + step_reward
          + joint_limits_reward / none_exe_reward / not_within_goal_space_reward

When ``multi_goal=True``, ``current_goal`` is the lift target
(``cube_init + [0, 0, lift_height]`` with
``lift_height = 0.15 m``) until ``intermediate_reached`` flips on
(when ``‖cube − intermediate_goal‖ < reach_tolerance``); after that,
``current_goal = pnp_goal``.

``grasp_finger_thresh = 0.30`` rad (knuckle floor — closed enough
to be grasping something). ``grasp_dist_thresh = 0.05`` m
(EE-to-cube ceiling).

Code example:

.. code-block:: python

   env = gym.make("UR5ePnPSim-v0", reward_type="Dense", multi_goal=True)
   env = gym.make("UR5ePnPGoalSim-v0", reward_type="Sparse", multi_goal=True)

Starting State
--------------

Joint pose: folded upright (same as :doc:`reach`). Gripper:
**OPEN** (``init_open_gripper = [0.0]`` rad — opposite of push,
where the gripper resets closed).

**Cube spawn.** 4 cm red cube at default ``(0.500, -0.150, 0.795)``
in world frame; randomised XY within the spawn box if
``random_cube_spawn=True``. The cube is removed and re-spawned each
reset.

**Goal sampling.** ``pnp_goal`` ∈ Box(3,) sampled from
``position_goal_min/max``. With ``multi_goal=True``,
``intermediate_goal = cube_init + [0, 0, 0.15]``.

Episode End
-----------

**Truncation.** ``max_episode_steps`` (default 100). Real env also
aborts on stale ``/joint_states``.

**Termination.** ``‖cube − pnp_goal‖ < reach_tolerance`` (sparse
path only).

Arguments
---------

Inherits all kwargs from :doc:`reach` and :doc:`push`, plus
pnp-specific:

.. list-table::
   :widths: 24 14 62
   :header-rows: 1

   * - Kwarg
     - Default
     - Meaning
   * - ``multi_goal``
     - ``True``
     - Enable the lift-then-place curriculum
       (``intermediate_goal`` reached → switch to ``pnp_goal``).
   * - ``lift_height``
     - ``0.15`` (m)
     - Vertical offset of the intermediate lift goal above the cube
       spawn position.

Version History
---------------

* ``v0`` — first release (``rl_environments`` v0.1.0). Inverted
  grasp comparison (``knuckle_pos > grasp_finger_thresh``) +
  single-element gripper publish — both UR5e-specific vs the
  prismatic-finger robots.
