Ready-made environments
=======================

The ``rl_environments`` repository ships pre-built ``gymnasium``
environments for several robots and tasks. This page lists what's
currently working out of the box. The matrix will grow as new task
implementations land.


Status legend
-------------

.. list-table::
   :widths: 12 88
   :header-rows: 1

   * - Symbol
     - Meaning
   * - ✓
     - Implemented and exercised by training/validation scripts in
       ``rl_training_validation``.
   * - ◐
     - Robot environment is in place; no task implementations or
       training scripts yet.
   * - —
     - Planned in the directory layout but not yet implemented.


Robot × task matrix
-------------------

.. list-table::
   :widths: 18 16 16 16 16 16
   :header-rows: 1

   * - Robot
     - Sim/reach
     - Sim/push
     - Sim/pnp
     - Real/reach
     - Real/(push,pnp)
   * - Trossen RX200
     - ✓
     - —
     - —
     - —
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


Trossen RX200 — simulation, reach
---------------------------------

The most exercised env in the ecosystem. Multiple variants cover
joint-position vs end-effector action spaces, with optional Kinect
v2 or ZED 2 cameras for vision-based observations.

Gymnasium IDs
~~~~~~~~~~~~~

**Base joint-position action space**

* ``RX200ReacherSim-v0`` — default joint-space reach.
* ``RX200ReacherSim-v1``, ``-v2`` — observation-space variants.
* ``RX200ReacherGoalSim-v0`` — goal-conditioned (for HER).

**End-effector action space**

* ``RX200ReacherEESim-v0`` — EE-space reach.
* ``RX200ReacherEEGoalSim-v0`` — goal-conditioned, EE-space.

**Kinect v2 vision**

* ``RX200kinectReacherSimRGB-v0`` — adds RGB observation.
* ``RX200kinectReacherSimRGBPlus-v0`` — RGB + state.
* ``RX200kinectReacherSimRGBDepthPlus-v0`` — RGB + depth + state.
* ``RX200kinectReacherEE*-v0`` — EE-space variants of each.
* ``RX200kinectReacherGoal*-v0`` — goal-conditioned variants.

**ZED 2 vision**

* ``RX200Zed2ReacherSimRGB-v0`` — adds RGB observation.
* ``RX200Zed2ReacherSimRGBPlus-v0``, ``-RGBDepthPlus-v0`` — richer obs.
* ``RX200Zed2ReacherEE*-v0`` — EE-space variants.
* ``RX200Zed2ReacherGoal*-v0`` — goal-conditioned variants.

Training scripts
~~~~~~~~~~~~~~~~

In ``rl_training_validation``:

* ``rx200/reach/rx200_reach_train_sim.py``
* ``rx200/reach/rx200_reach_validate_sim.py``

The training script ties together a ``gym.make(...)`` env, a config
file under ``rl_training_validation/config/``, and an SB3 algorithm
from ``sb3_ros_support``. See :doc:`training`.


Niryo Ned2 — simulation
-----------------------

Robot environments for Ned2 sim are in place, but task envs are
limited and no training scripts are wired up yet. If you want to
add a Ned2 reach env, the easiest starting point is the matching
RX200 reach env: copy, adjust joint counts / link names / DOF, and
register a new gymnasium ID. See :doc:`env_creation_sim`.


Universal Robots UR5
--------------------

UR5 directories exist in ``rl_environments`` and
``rl_training_validation`` but they are placeholders. Implementations
are planned. See :doc:`env_creation_sim` for the recommended starting
point if you want to add one.
