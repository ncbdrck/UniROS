UR5e — Reach
============

The arm must move its end-effector to a 3D target sampled in the
workspace above the cafe-table. No cube; the gripper is not commanded.
The achieved goal is the EE position; the desired goal is the
sampled target.

This page covers four registered Gymnasium env IDs:

* ``UR5eReacherSim-v0`` — standard, Gazebo
* ``UR5eReacherGoalSim-v0`` — goal-conditioned (HER), Gazebo
* ``UR5eReacherReal-v0`` — standard, real hardware
* ``UR5eReacherGoalReal-v0`` — goal-conditioned, real hardware

Description
-----------

A UR5e arm with a Robotiq 2F-85 gripper sits on a 4-legged
``ur5_base`` (top at z = 0.59) next to a ``cafe_table`` workspace at
world (0.7, 0, 0). The agent commands joint-space deltas (default)
or absolute joint positions, or alternatively end-effector position
deltas in EE mode (``ee_action_type=True``). Every commanded action
is checked link-by-link against the workspace floor before being
published — actions that would dip a link below the safety floor or
into the cafe-table footprint are rejected with a penalty reward.

The env loop runs at ``environment_loop_rate`` (default 10 Hz). In
real-time mode (``realtime_mode=True``, the default), Gazebo physics
is never paused; ``step()`` reads the latest cached obs / reward /
done values. Otherwise the standard MDP loop pauses physics around
each action.

Action Space
------------

**Joint mode** (default, ``ee_action_type=False``). Box(6,):

.. list-table::
   :widths: 6 28 12 12 30 12
   :header-rows: 1

   * - Num
     - Action
     - Min
     - Max
     - Joint
     - Unit
   * - 0
     - shoulder pan delta (or absolute, per ``delta_action``)
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

When ``delta_action=True`` (default), the action is scaled by
``delta_coeff = 0.05`` and added to the current joint position. When
``delta_action=False`` the action is the absolute joint target,
clipped to the box bounds.

**EE mode** (``ee_action_type=True``). Box(3,) — ΔEE position in
the robot's base frame:

.. list-table::
   :widths: 6 28 12 12 42
   :header-rows: 1

   * - Num
     - Action
     - Min
     - Max
     - Notes
   * - 0
     - Δx (or absolute x)
     - -0.90
     - 1.20
     - EE x in base_link frame
   * - 1
     - Δy (or absolute y)
     - -0.90
     - 0.90
     - EE y
   * - 2
     - Δz (or absolute z)
     - 0.00
     - 1.50
     - EE z

The env solves IK against the target EE pose, then publishes the
joint-space trajectory through the same per-link safety check as
joint mode.

Observation Space
-----------------

**Standard env (``UR5eReacherSim-v0`` / ``UR5eReacherReal-v0``).**
Box(27,) by default (24 if ``ee_action_type=True``):

.. list-table::
   :widths: 8 16 32 32 12
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
     - Unit vector EE → goal
     - normalized
     - unitless
   * - 6
     - 1
     - Euclidean distance EE → goal
     - ‖goal − ee‖
     - m
   * - 7–13
     - 7
     - Current joint positions
     - ``/ur5e/joint_states.position``
     - rad
   * - 14–19
     - 6 (or 3)
     - Previous action
     - cached
     - matches action space
   * - 20–26
     - 7
     - Current joint velocities
     - ``/ur5e/joint_states.velocity``
     - rad/s

The 7-element joint vectors are in alphabetical order from
``/joint_states``: ``elbow_joint``, ``robotiq_85_left_knuckle_joint``,
``shoulder_lift_joint``, ``shoulder_pan_joint``, ``wrist_1_joint``,
``wrist_2_joint``, ``wrist_3_joint``.

**Goal env (``UR5eReacherGoalSim-v0`` / ``UR5eReacherGoalReal-v0``).**
Gymnasium ``Dict`` with three keys:

``observation`` — Box(24,) (or 21 in EE mode). Same as the standard
env's Box minus the EE→goal feature columns (no goal info leaks into
the policy's plain observation).

``desired_goal`` — Box(3,). Sampled target XYZ in base frame:

.. list-table::
   :widths: 8 16 32 32 12
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
     - 0.85
     - 1.10

``achieved_goal`` — Box(3,). Current EE XYZ (same coordinate frame
as ``desired_goal``).

Rewards
-------

The env supports two reward modes selected by the ``reward_type``
kwarg.

**Sparse** (``reward_type="Sparse"``, required for HER on goal envs):

.. code-block:: text

   reward = 0.0  if ‖ee − goal‖ < reach_tolerance else -1.0

**Dense** (``reward_type="Dense"``, default for std env):

.. code-block:: text

   reward = -multiplier_dist_reward * ‖ee − goal‖   # step shaping
          + reached_goal_reward     if ‖ee − goal‖ < reach_tolerance
          + step_reward             every step
          + joint_limits_reward     if action outside joint bounds
          + none_exe_reward         if MoveIt plan / FK safety rejects
          + not_within_goal_space_reward  if goal sampling failed

Defaults (from ``config/ur5e_reach_task_config.yaml``):
``reach_tolerance=0.05``, ``multiplier_dist_reward=2.0``,
``reached_goal_reward=20``, ``step_reward=-0.5``,
``joint_limits_reward=-2.0``, ``none_exe_reward=-5.0``,
``not_within_goal_space_reward=-2.0``.

Code example:

.. code-block:: python

   import uniros as gym
   import rl_environments  # noqa: F401  (triggers registration)

   # Standard env, dense reward
   env = gym.make("UR5eReacherSim-v0", reward_type="Dense")
   # Goal env, sparse reward (HER)
   env = gym.make("UR5eReacherGoalSim-v0", reward_type="Sparse")

Starting State
--------------

Initial joint pose (folded upright, set via
``gazebo_msgs/SetModelConfiguration`` while Gazebo is paused, then
unpaused):

.. code-block:: text

   shoulder_pan_joint  =  0.000
   shoulder_lift_joint = -1.5707  (-90°, upper arm vertical up)
   elbow_joint         =  1.5707  (+90°, forearm horizontal forward)
   wrist_1_joint       = -1.5707
   wrist_2_joint       = -1.5707
   wrist_3_joint       =  0.000

The arm's all-zeros URDF pose puts it horizontal at base height
(z = 0.59), colliding with the cafe-table column at x = 0.7. The
folded pose above puts the EE over the workspace at roughly
(0.40, 0, 0.95) in world coordinates.

**Goal sampling.** Each ``reset()`` draws a fresh
``desired_goal`` ∈ Box(3,) from
``[position_goal_min, position_goal_max]``:

.. code-block:: text

   x ∈ [0.40, 0.80]   y ∈ [-0.30, 0.30]   z ∈ [0.85, 1.10]

This box sits above the cafe-table top (z = 0.775) and within the
UR5e's ≈ 0.85 m reach from the arm base at (0, 0, 0.59).

Episode End
-----------

**Truncation.** Episodes truncate after ``max_episode_steps`` (default
100, set at registration time; override via the ``TimeLimitWrapper``
in the train scripts). Episodes also terminate / truncate if the
joint-state staleness gate fires on the real env (``/joint_states``
not updated for ``joint_state_timeout_s = 0.5`` seconds).

**Termination.** Episode terminates when the EE reaches the goal
(``‖ee − goal‖ < reach_tolerance``). Termination is *only* set on the
sparse-reward path; on dense reward the agent keeps accumulating the
shaping signal even after reaching the goal until the time limit.

Arguments
---------

Top-level kwargs to ``gym.make("UR5eReacher*-v0", ...)``. All have
sensible defaults; only ``gazebo_gui`` and ``reward_type`` are
commonly overridden.

.. list-table::
   :widths: 24 14 62
   :header-rows: 1

   * - Kwarg
     - Default
     - Meaning
   * - ``seed``
     - ``None``
     - RNG seed for goal sampling.
   * - ``gazebo_gui``
     - ``False``
     - Set ``True`` to launch Gazebo with the GUI.
   * - ``reward_type``
     - ``"Dense"`` (std) / ``"Sparse"`` (goal)
     - One of ``"Sparse"`` or ``"Dense"``.
   * - ``ee_action_type``
     - ``False``
     - ``True`` → Box(3,) EE action; ``False`` → Box(6,) joint action.
   * - ``delta_action``
     - ``True``
     - ``True`` → action interpreted as delta (× ``delta_coeff``);
       ``False`` → action is the absolute target.
   * - ``delta_coeff``
     - ``0.05``
     - Scale factor when ``delta_action=True``.
   * - ``environment_loop_rate``
     - ``10.0``
     - Hz for the internal env loop / obs cache update.
   * - ``action_cycle_time``
     - ``0.5``
     - Seconds the env waits between actions. Must be ≥ 1 /
       ``environment_loop_rate``.
   * - ``action_speed``
     - ``0.2`` (sim) / configurable (real)
     - Time the controller has to interpolate to the commanded joint
       target.
   * - ``realtime_mode``
     - ``True``
     - ``True`` → UniROS real-time loop (physics never paused).
       ``False`` → MDP-style pause-step-resume.
   * - ``use_kinect``
     - ``False``
     - Opt-in subscribe to ``/head_mount_kinect2/*`` for RGB / depth.
   * - ``log_internal_state``
     - ``False``
     - Verbose ``rospy.loginfo`` for debugging.

Real-only kwargs (``UR5eReacher*Real-v0``): inherits the above plus
the ``--allow-real-robot-motion`` gate enforced by
``rl_training_validation.utils.env_safety.check_env_constructable``.

Version History
---------------

* ``v0`` — first release (``rl_environments`` v0.1.0). Per-link FK
  safety check; ``SetModelConfiguration`` init-pose path; 27-dim
  Box obs (standard) or 24-dim Box + 3-dim Box × 2 (goal).
