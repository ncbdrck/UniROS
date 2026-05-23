NED2 (Niryo Ned2)
=================

The `Niryo Ned2 <https://niryo.com/product/educational-desktop-robotic-arm/>`_
is a 6-DoF tabletop arm with a 2-mors prismatic gripper (binary
open/close API on real hardware via ``niryo_robot_tools_commander``;
direct trajectory publish in sim). In our setup it is mounted on
the same cafe-table the RX200 uses, with a head-mount Kinect v2 and
an opt-in wrist camera (Niryo's built-in tool camera).

Tasks
-----

.. list-table::
   :widths: 14 30 56
   :header-rows: 1

   * - Task
     - Env ids
     - Page
   * - **Reach**
     - ``NED2ReacherSim-v0`` / ``...GoalSim-v0`` / ``...Real-v0`` /
       ``...GoalReal-v0``
     - :doc:`reach`
   * - **Push**
     - ``NED2PushSim-v0`` / ``...GoalSim-v0`` / ``...Real-v0`` /
       ``...GoalReal-v0``
     - :doc:`push`
   * - **PnP**
     - ``NED2PnPSim-v0`` / ``...GoalSim-v0`` / ``...Real-v0`` /
       ``...GoalReal-v0``
     - :doc:`pnp`

Robot-specific facts
--------------------

.. list-table::
   :widths: 28 72
   :header-rows: 1

   * - Topic
     - Value
   * - Arm joints (6)
     - ``joint_1`` … ``joint_6`` (Niryo's standard naming)
   * - Gripper joints (2)
     - ``joint_base_to_mors_1``, ``joint_base_to_mors_2`` (prismatic,
       ± 0.01 m stroke = 20 mm total)
   * - Gripper command API
     - Binary ``"open"`` / ``"close"`` on real (via
       ``niryo_robot_tools_commander``); direct trajectory publish to
       ``/gazebo_tool_commander/follow_joint_trajectory`` in sim
   * - PnP joint-mode action dim
     - 6 (arm) + 1 (gripper scalar) = 7
   * - Arm controller topic
     - ``/niryo_robot_follow_joint_trajectory_controller/command``
   * - URDF link prefix
     - Bare names on both sim + real (``base_link``,
       ``shoulder_link``, …, ``tool_link``)
   * - End-effector link (FK)
     - ``tool_link`` (MoveIt SRDF group ``arm`` ends here)
   * - Reference frame
     - ``base_link``
   * - Wrist camera (opt-in)
     - ``use_wrist_camera=True`` exposes ``self.cv_image_wrist``;
       sim topic ``/gazebo_camera/image_raw``, real topic
       ``/niryo_robot_vision/compressed_video_stream``
   * - Joint-1 safety bound
     - YAML uses ``±2.949`` (vs URDF ``±3.000``) for a 0.05 rad margin

Sim setup
---------

* Description-extras package: ``niryo_ned2_description_extras`` (URDF
  wrap, controller config, Kinect mount). ``ros_control`` uses
  ``EffortJointInterface`` so PID gains under
  ``/ned2/gazebo_ros_control/pid_gains/joint_*`` are loaded to the
  rosparam server *before* the model spawns.
* Two URDF variants: ``ned2_kinect.urdf.xacro`` (reach / push) and
  ``ned2_kinect_gripper.urdf.xacro`` (pnp). Selected via
  ``gripper:=true|false`` arg on the gazebo launch.

Real setup
----------

* Bring up ``niryo_robot_bringup`` on the Ned2's network IP.
* The env subscribes to ``/ned2/joint_states`` and publishes to
  ``/ned2/niryo_robot_follow_joint_trajectory_controller/command``.
* Push / PnP subscribe to ``/cube_pose`` for cube tracking.

.. toctree::
   :hidden:
   :maxdepth: 1

   reach
   push
   pnp
