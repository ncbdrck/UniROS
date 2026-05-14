Ready-made environments
=======================

The ``rl_environments`` repository ships pre-built ``gymnasium``
environments for several robots and tasks. This page is a precise
inventory of what's currently implemented, registered, and tested
— so you know what works out of the box versus what's scaffolding.

The matrix will grow as more task implementations land.


Status legend
-------------

.. list-table::
   :widths: 24 76
   :header-rows: 1

   * - Symbol
     - Meaning
   * - ✓
     - Implemented (code + gymnasium ID registered).
   * - ◐
     - Partial: source files exist in the directory layout, but no
       gymnasium IDs are registered for this task on this robot.
   * - —
     - Empty placeholder in the directory layout.


Robot × task implementation matrix
----------------------------------

Whether the task env class exists and whether the gym ID is
registered in ``rl_environments/__init__.py``.

.. list-table::
   :widths: 20 14 14 14 14 14
   :header-rows: 1

   * - Robot
     - Sim/reach
     - Sim/push
     - Sim/pnp
     - Real/reach
     - Real/(push,pnp)
   * - Trossen RX200
     - ✓
     - ✓
     - —
     - ✓
     - —
   * - Niryo Ned2
     - ◐
     - —
     - —
     - —
     - —
   * - Universal UR5
     - —
     - —
     - —
     - —
     - —


Training script availability
----------------------------

Whether ``rl_training_validation`` contains a working
``{robot}_{task}_train_*.py`` and/or
``{robot}_{task}_validate_*.py`` script that wires the env to an
``sb3_ros_support`` algorithm + a YAML config.

.. list-table::
   :widths: 20 14 14 14 14 14
   :header-rows: 1

   * - Robot / task
     - Train sim
     - Validate sim
     - Train real
     - Validate real
     - Joint sim+real
   * - RX200 reach
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓ (multi-task)
   * - RX200 push
     - ✓
     - —
     - —
     - —
     - —

Other robot/task combinations don't have training scripts yet.


Trossen RX200 — simulation, reach
---------------------------------

The most exercised path in the ecosystem and the basis for the
benchmark experiments in the paper. Multiple variants cover
joint-position vs end-effector action spaces, with optional
Kinect v2 or ZED 2 cameras for vision-based observations.

Registered gymnasium IDs
~~~~~~~~~~~~~~~~~~~~~~~~

**Joint-position action space**

* ``RX200ReacherSim-v0``, ``-v1``, ``-v2`` — observation-space variants.
* ``RX200ReacherGoalSim-v0`` — goal-conditioned (use with HER).

**End-effector action space**

* ``RX200ReacherEESim-v0``
* ``RX200ReacherEEGoalSim-v0``

**Kinect v2 vision** (RGB / RGB+state / RGB+depth+state, each in
joint-space and EE-space variants, each with optional goal-conditioning)

* ``RX200kinectReacherSimRGB-v0`` and family
* ``RX200kinectReacherEESimRGB-v0`` and family
* ``RX200kinectReacherGoalSimRGB-v0`` and family
* ``RX200kinectReacherEEGoalSimRGB-v0`` and family

**ZED 2 vision** (same RGB / RGB+state / RGB+depth+state variants)

* ``RX200Zed2ReacherSimRGB-v0`` and family
* (same matrix of EE / Goal / Plus / DepthPlus suffixes)

Training scripts
~~~~~~~~~~~~~~~~

In ``rl_training_validation/src/rl_training_validation/rx200/reach/``:

* ``rx200_reach_train_sim.py``
* ``rx200_reach_validate_sim.py``

See :doc:`training` for how these tie a gym ID to an
``sb3_ros_support`` algorithm and a YAML config.


Trossen RX200 — simulation, push
--------------------------------

Registered gymnasium IDs
~~~~~~~~~~~~~~~~~~~~~~~~

* ``RX200PushSim-v0``, ``-v1`` — joint-space push variants.
* ``RX200PushEESim-v0`` — EE-space push.
* ``RX200kinectPushSimRGB-v0`` and the matching RGB / RGB+state /
  RGB+depth+state and EE-space variants.

Training script
~~~~~~~~~~~~~~~

* ``rx200/push/rx200_push_train_sim.py`` (sim only; no validation
  script yet).


Trossen RX200 — real hardware, reach
------------------------------------

Registered gymnasium IDs
~~~~~~~~~~~~~~~~~~~~~~~~

* ``RX200ReacherReal-v0`` — joint-space reach.
* ``RX200ReacherGoalReal-v0`` — goal-conditioned, for HER.

Training scripts
~~~~~~~~~~~~~~~~

In ``rl_training_validation/src/rl_training_validation/rx200/reach/``:

* ``rx200_reach_train_real.py``
* ``rx200_reach_validate_real.py``

These pair with the matching sim scripts above so a sim-trained
policy can be validated directly on hardware (Use Case B in the
paper) or co-trained across both domains (Use Case C; see
:doc:`joint_sim_real_training`).


Niryo Ned2
----------

Robot env source files exist for Ned2 sim, but no gymnasium IDs
are registered and no training scripts are wired up. If you want
to add a Ned2 reach env, the easiest path is to copy the matching
RX200 reach env, adjust joint count / link names / DOF, and
register a new gymnasium ID. See :doc:`env_creation_sim`.


Universal Robots UR5
--------------------

UR5 directories exist in ``rl_environments`` and
``rl_training_validation`` but they are placeholders today. No
gymnasium IDs are registered and no training scripts exist. See
:doc:`env_creation_sim` for the recommended starting point.
