sb3_ros_support API reference
=============================

Stable Baselines 3 algorithm wrappers configured for ROS-based
training scripts. Each algorithm subclasses
:class:`sb3_ros_support.core.BasicModel` and exposes a uniform
``train`` / ``validate`` / ``save`` / ``load`` surface, so swapping
PPO for SAC for TD3 is a configuration edit, not a code rewrite.


.. contents::
   :local:
   :depth: 2


Base model
----------

.. automodule:: sb3_ros_support.core
   :members:
   :show-inheritance:


Algorithms
----------

PPO
~~~

.. automodule:: sb3_ros_support.ppo
   :members:
   :show-inheritance:


A2C
~~~

.. automodule:: sb3_ros_support.a2c
   :members:
   :show-inheritance:


DDPG
~~~~

.. automodule:: sb3_ros_support.ddpg
   :members:
   :show-inheritance:


TD3
~~~

.. automodule:: sb3_ros_support.td3
   :members:
   :show-inheritance:


SAC
~~~

.. automodule:: sb3_ros_support.sac
   :members:
   :show-inheritance:


DQN
~~~

.. automodule:: sb3_ros_support.dqn
   :members:
   :show-inheritance:


Goal-conditioned variants (HER)
-------------------------------

DDPG_GOAL
~~~~~~~~~

.. automodule:: sb3_ros_support.ddpg_goal
   :members:
   :show-inheritance:


TD3_GOAL
~~~~~~~~

.. automodule:: sb3_ros_support.td3_goal
   :members:
   :show-inheritance:


SAC_GOAL
~~~~~~~~

.. automodule:: sb3_ros_support.sac_goal
   :members:
   :show-inheritance:


DQN_GOAL
~~~~~~~~

.. automodule:: sb3_ros_support.dqn_goal
   :members:
   :show-inheritance:


Utilities
---------

.. automodule:: sb3_ros_support.utils.sb3_common
   :members:
   :show-inheritance:


.. automodule:: sb3_ros_support.utils.yaml_utils
   :members:
   :show-inheritance:
