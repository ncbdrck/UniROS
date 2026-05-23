VX300S (Trossen ViperX-300 S)
=============================

The `Trossen ViperX-300 S <https://docs.trossenrobotics.com/interbotix_xsarms_docs/specifications/vx300s.html>`_
is a 6-DoF tabletop arm — larger and longer-reach than its RX200
sibling (≈ 750 mm vs 550 mm) with the same two-prismatic-finger
gripper under continuous position control. Flush-mounted on the
same cafe-table the RX200 uses; head-mount Kinect v2 in sim.

Tasks
-----

.. list-table::
   :widths: 14 30 56
   :header-rows: 1

   * - Task
     - Env ids
     - Page
   * - **Reach**
     - ``VX300SReacherSim-v0`` / ``...GoalSim-v0`` / ``...Real-v0``
       / ``...GoalReal-v0``
     - :doc:`reach`
   * - **Push**
     - ``VX300SPushSim-v0`` / ``...GoalSim-v0`` / ``...Real-v0`` /
       ``...GoalReal-v0``
     - :doc:`push`
   * - **PnP**
     - ``VX300SPnPSim-v0`` / ``...GoalSim-v0`` / ``...Real-v0`` /
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
     - ``waist``, ``shoulder``, ``elbow``, ``forearm_roll``,
       ``wrist_angle``, ``wrist_rotate``
   * - Gripper joints (2)
     - ``left_finger``, ``right_finger`` (prismatic, continuous;
       wider stroke than RX200 — left ∈ [0.021, 0.057], right ∈
       [-0.057, -0.021])
   * - Gripper open value (PnP)
     - ``gripper_max`` (≈ 0.057 m left-finger position)
   * - Gripper closed value
     - ``gripper_min`` (≈ 0.021 m); ``grasp_finger_thresh = 0.024``
   * - PnP joint-mode action dim
     - 6 (arm) + 1 (gripper) = 7
   * - Arm controller topic
     - ``/vx300s/arm_controller/command`` (sim) / interbotix driver
       (real)
   * - URDF link prefix
     - ``vx300s/`` on every link (sim + real)
   * - End-effector link (FK)
     - ``vx300s/ee_gripper_link``
   * - Reference frame
     - ``vx300s/base_link``
   * - MoveIt planning groups
     - ``interbotix_arm``, ``interbotix_gripper``
   * - Goal x_min
     - 0.20 (bumped from 0.15 — VX300S near-base dead-zone shifts
       further out than RX200's)

Sim setup
---------

* Description-extras package: ``viperx300s_description`` (URDF wrap,
  table + cube models, Kinect mount, controller config).
* The env launches Gazebo with the cafe-table at x = 0.2 and the
  arm flush at z = 0.78. Interbotix MoveIt under ``/vx300s`` with
  ``dof:=6``.

Real setup
----------

* Bring up the Interbotix hardware driver
  (``xsarm_moveit_interface.launch``) with
  ``robot_model:=vx300s dof:=6 use_actual:=true``.
* Same ``/cube_pose`` fallback contract as RX200 / NED2 for push / pnp.

.. toctree::
   :hidden:
   :maxdepth: 1

   reach
   push
   pnp
