Environments
============

The ``rl_environments`` package ships pre-built Gymnasium environments
for four manipulator arms and three manipulation tasks. Each
``(robot, task)`` combination is registered as four env IDs covering
the cross-product of {standard, goal-conditioned} × {simulation,
real}, giving **48 task env IDs** plus extra Kinect/ZED2 sensor
variants for RX200 (54 total).

All envs are standard Gymnasium ``gym.Env`` instances. Standard envs
use a ``Box`` observation space; goal-conditioned envs use the
Gymnasium ``GoalEnv`` ``Dict`` shape with ``observation`` /
``desired_goal`` / ``achieved_goal`` keys (suitable for HER replay
buffers).

Robots
------

.. list-table::
   :widths: 18 12 18 18 34
   :header-rows: 1

   * - Robot
     - DoF
     - Gripper
     - Mount
     - Tasks
   * - :doc:`rx200/index` — Trossen ReactorX-200
     - 5
     - 2 prismatic fingers (continuous)
     - Flush on cafe-table
     - Reach, Push, PnP
   * - :doc:`ned2/index` — Niryo Ned2
     - 6
     - 2 prismatic mors (binary open/close)
     - Flush on cafe-table
     - Reach, Push, PnP
   * - :doc:`vx300s/index` — Trossen ViperX-300 S
     - 6
     - 2 prismatic fingers (continuous)
     - Flush on cafe-table
     - Reach, Push, PnP
   * - :doc:`ur5e/index` — Universal Robots UR5e + Robotiq 2F-85
     - 6
     - 1 knuckle (continuous, mimic linkage)
     - 4-legged base + separate cafe-table
     - Reach, Push, PnP

Tasks
-----

Every robot supports the same three tasks. The same task on different
robots shares its reward shape, observation layout, and command
interface — only the joint count, gripper mechanics, and workspace
geometry differ.

.. list-table::
   :widths: 14 86
   :header-rows: 1

   * - Task
     - Goal
   * - **Reach**
     - The end-effector must reach a 3D target sampled in the
       workspace. No cube. Gripper is not commanded. Goal is in the
       air; achieved goal is the EE position.
   * - **Push**
     - A cube sits on the cafe-table. The closed gripper acts as a
       flat paddle; the arm must push the cube to a goal point on the
       table. Gripper is not in the action vector. Achieved goal is
       the cube position.
   * - **Pick-and-Place** (PnP)
     - A cube sits on the cafe-table. The action vector gains one
       extra scalar — an absolute gripper command. The arm must grasp
       the cube, lift it, and place it at a goal point (which can be
       in the air). Optional ``multi_goal`` curriculum splits the
       reward into a lift target then the final place target.
       Achieved goal is the cube position.

Variants — every (robot, task) is registered four ways
-------------------------------------------------------

.. list-table::
   :widths: 24 76
   :header-rows: 1

   * - Variant
     - Description
   * - ``{Robot}{Task}Sim-v0``
     - Standard, Gazebo simulation. Box observation space.
   * - ``{Robot}{Task}GoalSim-v0``
     - Goal-conditioned, Gazebo. Dict observation space. Pair with
       HER (``sb3_ros_support.td3_goal``).
   * - ``{Robot}{Task}Real-v0``
     - Standard, real hardware. Same observation shape as the sim
       variant; real-side machinery for joint-state staleness gate +
       cube-pose subscriber for push/pnp.
   * - ``{Robot}{Task}GoalReal-v0``
     - Goal-conditioned, real hardware.

Common safety machinery
-----------------------

Every env enforces a per-link forward-kinematics safety check before
publishing a joint trajectory. Each candidate joint target is
forward-kinematic'd through PyKDL subchains for every safety-check
link; if any link's predicted world-z falls below the workspace
floor, the action is rejected and a penalty reward is returned. For
robots mounted flush on the cafe-table (RX200 / NED2 / VX300S) the
floor is the table surface; UR5e adds a second check against the
cafe-table footprint because it sits on a separate base.

All real-side trainers refuse to construct unless ``--allow-real-robot-motion``
is passed on the CLI. The flag exports ``ALLOW_REAL_ROBOT_MOTION=1``
in the process so subprocess workers inherit the same consent — it
is propagation of the flag, not a second independent channel.

.. toctree::
   :hidden:
   :maxdepth: 2

   rx200/index
   ned2/index
   vx300s/index
   ur5e/index

Reference
---------

If you use these environments in your research, please cite the
UniROS paper:

.. code-block:: bibtex

   @Article{s25185679,
     AUTHOR  = {Kapukotuwa, Jayasekara and Lee, Brian and Devine, Declan and Qiao, Yuansong},
     TITLE   = {UniROS: ROS-Based Reinforcement Learning Across Simulated and Real-World Robotics},
     JOURNAL = {Sensors},
     VOLUME  = {25},
     YEAR    = {2025},
     NUMBER  = {18},
     PAGES   = {5679},
     DOI     = {10.3390/s25185679},
   }
