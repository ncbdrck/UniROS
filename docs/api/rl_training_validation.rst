rl_training_validation API reference
====================================

Training and validation scripts for the pre-built environments in
``rl_environments``. Each script wires a ``gym.make()`` env to an
``sb3_ros_support`` algorithm wrapper and a YAML config file.

For the user-facing training guide see :doc:`/guides/training`.

.. note::

   This page covers the reach training/validation scripts across
   all four supported robots plus the multi-task learning script.
   The push and pick-and-place scripts share docstring patterns
   with their underlying task envs and are intentionally omitted
   while those docstrings are tidied — the scripts themselves are
   shipped and runnable from the source tree. See
   :doc:`/guides/training` for the user-facing inventory.


.. contents::
   :local:
   :depth: 2


Top-level package
-----------------

.. automodule:: rl_training_validation
   :members:
   :show-inheritance:


Utilities
---------

env_safety
~~~~~~~~~~

Real-robot motion consent gate
(``--allow-real-robot-motion``), env-ID parsing helpers, and the
registry-introspection helpers used by the ``scripts/`` smoke tools.

.. automodule:: rl_training_validation.utils.env_safety
   :members:
   :show-inheritance:


MultiTaskEnv
~~~~~~~~~~~~

Wrapper for training a single policy across several task envs in
one process. Used by the multi-task training scripts below.

.. automodule:: rl_training_validation.utils.multi_task_env
   :members:
   :show-inheritance:


MultiTaskGoalEnv
~~~~~~~~~~~~~~~~

Goal-conditioned variant of :class:`MultiTaskEnv`, routes HER
reward recomputation per sub-env via ``info["task_id"]``.

.. automodule:: rl_training_validation.utils.multi_task_goal_env
   :members:
   :show-inheritance:


RX200 — Reach
-------------

Sim training / validation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: rl_training_validation.rx200.reach.rx200_reach_train_sim
   :members:
   :show-inheritance:


.. automodule:: rl_training_validation.rx200.reach.rx200_reach_validate_sim
   :members:
   :show-inheritance:


Real training / validation
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: rl_training_validation.rx200.reach.rx200_reach_train_real
   :members:
   :show-inheritance:


.. automodule:: rl_training_validation.rx200.reach.rx200_reach_validate_real
   :members:
   :show-inheritance:


Niryo Ned2 — Reach
------------------

Sim training / validation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: rl_training_validation.ned2.reach.ned2_reach_train_sim
   :members:
   :show-inheritance:


.. automodule:: rl_training_validation.ned2.reach.ned2_reach_validate_sim
   :members:
   :show-inheritance:


Real training / validation
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: rl_training_validation.ned2.reach.ned2_reach_train_real
   :members:
   :show-inheritance:


.. automodule:: rl_training_validation.ned2.reach.ned2_reach_validate_real
   :members:
   :show-inheritance:


Trossen VX300S — Reach
----------------------

Sim training / validation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: rl_training_validation.vx300s.reach.vx300s_reach_train_sim
   :members:
   :show-inheritance:


.. automodule:: rl_training_validation.vx300s.reach.vx300s_reach_validate_sim
   :members:
   :show-inheritance:


Real training / validation
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: rl_training_validation.vx300s.reach.vx300s_reach_train_real
   :members:
   :show-inheritance:


.. automodule:: rl_training_validation.vx300s.reach.vx300s_reach_validate_real
   :members:
   :show-inheritance:


Universal Robots UR5e — Reach
-----------------------------

Sim training / validation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: rl_training_validation.ur5e.reach.ur5e_reach_train_sim
   :members:
   :show-inheritance:


.. automodule:: rl_training_validation.ur5e.reach.ur5e_reach_validate_sim
   :members:
   :show-inheritance:


Real training / validation
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: rl_training_validation.ur5e.reach.ur5e_reach_train_real
   :members:
   :show-inheritance:


.. automodule:: rl_training_validation.ur5e.reach.ur5e_reach_validate_real
   :members:
   :show-inheritance:


Multi-task learning
-------------------

.. automodule:: rl_training_validation.multi_task_learning.multi_train_sim
   :members:
   :show-inheritance:
