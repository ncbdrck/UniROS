UR5e (Universal Robots UR5e + Robotiq 2F-85)
=============================================

The `Universal Robots UR5e <https://www.universal-robots.com/products/ur5-robot/>`_
is a 6-DoF collaborative arm with a `Robotiq 2F-85 <https://robotiq.com/products/2f-adaptive-robot-gripper/>`_
parallel-jaw gripper. Unlike the other three robots, the UR5e is
mounted on a 4-legged ``ur5_base`` (top plate at z = 0.59) with a
SEPARATE ``cafe_table`` workspace at world (0.7, 0, 0) — the arm
sits next to the table, not on top of it.

Tasks
-----

.. list-table::
   :widths: 14 30 56
   :header-rows: 1

   * - Task
     - Env ids
     - Page
   * - **Reach**
     - ``UR5eReacherSim-v0`` / ``...GoalSim-v0`` / ``...Real-v0`` /
       ``...GoalReal-v0``
     - :doc:`reach`
   * - **Push**
     - ``UR5ePushSim-v0`` / ``...GoalSim-v0`` / ``...Real-v0`` /
       ``...GoalReal-v0``
     - :doc:`push`
   * - **PnP**
     - ``UR5ePnPSim-v0`` / ``...GoalSim-v0`` / ``...Real-v0`` /
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
     - ``shoulder_pan_joint``, ``shoulder_lift_joint``,
       ``elbow_joint``, ``wrist_1_joint``, ``wrist_2_joint``,
       ``wrist_3_joint``
   * - Gripper joints (1)
     - ``robotiq_85_left_knuckle_joint`` — single actuated knuckle;
       the other 5 finger joints follow via URDF mimic linkage
   * - Gripper open / closed value
     - **Open = gripper_min** ≈ 0.0 rad; **closed = gripper_max** ≈
       0.8 rad. *Opposite* of the prismatic-finger convention used by
       RX200 / VX300S where open = ``gripper_max``. The env reads
       ``gripper_open_value`` / ``gripper_closed_value`` rosparams so
       reward + obs code doesn't have to know which way the bounds map.
   * - ``grasp_finger_thresh`` semantics
     - INVERTED — ``is_grasped`` triggers when
       ``knuckle_pos > grasp_finger_thresh`` (≈ 0.4 rad)
   * - PnP joint-mode action dim
     - 6 (arm) + 1 (gripper scalar) = 7
   * - Arm controller topic
     - ``/ur5e/arm_controller/command``
   * - URDF link prefix
     - Bare names on both sim + real (``base_link``,
       ``shoulder_link``, …, ``ee_link``). MoveIt SRDF group ``arm``
       chains ``base_link → ee_link``.
   * - End-effector link (FK)
     - ``ee_link``
   * - Reference frame
     - ``base_link``
   * - MoveIt planning groups
     - ``arm``, ``gripper`` (from
       ``ur5e_robotiq_85_moveit_config`` SRDF)
   * - Init pose
     - Folded upright (``[0, -π/2, π/2, -π/2, -π/2, 0]``). The
       URDF-zero pose puts the arm horizontal at base height,
       colliding with the cafe-table column — sim uses
       ``SetModelConfiguration`` (pause → snap → unpause) to apply
       the safe pose before physics runs.
   * - Safety geometry
     - Two-floor check: every link clears ``base_z = 0.59`` AND
       only when projected over the cafe-table footprint, also
       clears ``table_top_z = 0.775``. Other robots have a single
       table floor since they're flush-mounted.

Sim setup
---------

* Description-extras package: ``ur5e_description_extras`` (URDF
  wrap, controller config, ``ur5_base`` model, ``cafe_table`` model,
  ``red_cube`` model, Kinect mount, ``ur5e_scene.world``).
* The env launches Gazebo with ``ur5e_scene.world`` (sun, ground,
  ur5_base, cafe_table baked in). Arm spawns at z = 0.59 on top of
  the base. MoveIt comes up via the
  ``ur5e_description_extras/launch/ur5e_move_group.launch`` wrapper
  (drops the un-namespaced upstream ``ur5e_robotiq_85_moveit_config``
  into ``<group ns="ur5e">``).

Real setup
----------

* TBD: ``ur5e_description_extras/launch/ur5e_real.launch`` (to write
  at the lab). Expected to bring up ``ur_robot_driver`` with the
  calibrated UR5e network IP + a Robotiq 2F-85 driver + MoveIt under
  ``/ur5e``.
* The env subscribes to ``/ur5e/joint_states`` and publishes to
  ``/ur5e/arm_controller/command`` + ``/ur5e/gripper_controller/command``.
* Push / PnP subscribe to ``/cube_pose`` for cube tracking.

.. toctree::
   :hidden:
   :maxdepth: 1

   reach
   push
   pnp
