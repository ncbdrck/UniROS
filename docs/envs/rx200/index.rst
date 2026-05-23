RX200 (Trossen ReactorX-200)
============================

The `Trossen ReactorX-200 <https://www.trossenrobotics.com/reactorx-200-robot-arm.aspx>`_
is a 5-DoF tabletop arm with two prismatic gripper fingers (left and
right) under continuous position control. In our setup it is
flush-mounted on a ``cafe_table`` (top at z = 0.78), with a head-mount
Kinect v2 (or ZED 2 for extra sim variants) providing optional
vision observations.

The RX200 is the framework's reference robot. Three tasks are
implemented (Reach, Push, PnP), each with standard + goal-conditioned
variants, in both Gazebo simulation and on real hardware.

Tasks
-----

.. list-table::
   :widths: 14 30 56
   :header-rows: 1

   * - Task
     - Env ids
     - Page
   * - **Reach**
     - ``RX200ReacherSim-v0`` / ``...GoalSim-v0`` /
       ``...Real-v0`` / ``...GoalReal-v0`` (+ ``RX200Zed2...`` sim
       variants)
     - :doc:`reach`
   * - **Push**
     - ``RX200PushSim-v0`` / ``...GoalSim-v0`` /
       ``...Real-v0`` / ``...GoalReal-v0``
     - :doc:`push`
   * - **PnP**
     - ``RX200PnPSim-v0`` / ``...GoalSim-v0`` /
       ``...Real-v0`` / ``...GoalReal-v0``
     - :doc:`pnp`

Robot-specific facts
--------------------

.. list-table::
   :widths: 28 72
   :header-rows: 1

   * - Topic
     - Value
   * - Arm joints (5)
     - ``waist``, ``shoulder``, ``elbow``, ``wrist_angle``, ``wrist_rotate``
   * - Gripper joints (2)
     - ``left_finger``, ``right_finger`` (prismatic, continuous;
       ``right_finger = -left_finger`` when commanded)
   * - Gripper open value (PnP)
     - ``gripper_max`` (≈ 0.037 m left-finger position)
   * - Gripper closed value
     - ``gripper_min`` (≈ 0.015 m); ``grasp_finger_thresh = 0.020`` —
       ``is_grasped`` triggers when ``left_finger_pos < grasp_finger_thresh``
   * - PnP joint-mode action dim
     - 5 (arm) + 1 (gripper) = 6
   * - Arm controller topic
     - ``/arm_controller/command`` (sim) / interbotix driver (real)
   * - URDF link prefix
     - ``rx200/`` on every link (sim + real)
   * - End-effector link (FK)
     - ``rx200/ee_arm_link``
   * - Reference frame
     - ``rx200/base_link``
   * - MoveIt planning groups
     - ``interbotix_arm``, ``interbotix_gripper``
   * - Sim sensor variants
     - Kinect v2 (default) or ZED 2 — selected by env-id prefix
       (``RX200...`` vs ``RX200Zed2...``). ZED variants exist for sim
       only.

Sim setup
---------

* Description-extras package: ``reactorx200_description`` (URDF
  wrap, table model, controller config, Kinect mount).
* The env launches its own Gazebo via ``multiros.utils.gazebo_core``,
  spawns the arm flush on the cafe-table at z = 0.78, and brings up
  Interbotix MoveIt under ``/rx200``.

Real setup
----------

* Bring up the Interbotix hardware driver
  (``interbotix_xsarm_moveit_interface/launch/xsarm_moveit_interface.launch``)
  with ``robot_model:=rx200 dof:=5 use_actual:=true``.
* The env subscribes to ``/rx200/joint_states`` and publishes joint
  trajectories to ``/rx200/arm_controller/command``.
* Push / PnP additionally subscribe to ``/cube_pose``
  (``geometry_msgs/PoseStamped``); without an external publisher the
  env falls back to the YAML ``cube_init_pos`` and emits a throttled
  warning. See :doc:`/guides/quickstart` for the
  ``rl_envs_cube_tracker`` AprilTag publisher.

.. toctree::
   :hidden:
   :maxdepth: 1

   reach
   push
   pnp
