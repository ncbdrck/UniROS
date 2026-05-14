rl_training_validation API reference
====================================

Training and validation scripts for the pre-built environments in
``rl_environments``. Each script wires a ``gym.make()`` env to an
``sb3_ros_support`` algorithm wrapper and a YAML config file.

For the user-facing training guide see :doc:`/guides/training`.


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


RX200 reach scripts
-------------------

Sim training / validation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: rl_training_validation.rx200.reach.rx200_reach_train_sim
   :members:
   :show-inheritance:


.. automodule:: rl_training_validation.rx200.reach.rx200_reach_validate_sim
   :members:
   :show-inheritance:


Real-hardware training / validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: rl_training_validation.rx200.reach.rx200_reach_train_real
   :members:
   :show-inheritance:


.. automodule:: rl_training_validation.rx200.reach.rx200_reach_validate_real
   :members:
   :show-inheritance:


Multi-task learning
-------------------

.. automodule:: rl_training_validation.multi_task_learning.multi_train_sim
   :members:
   :show-inheritance:
