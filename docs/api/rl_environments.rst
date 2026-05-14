rl_environments API reference
=============================

Pre-built ``gymnasium`` environments for the robots and tasks the
ecosystem currently supports. The package is organised as
``rl_environments/{robot}/{sim,real}/{robot_envs,task_envs}/...``.

For the user-facing list of working environments see
:doc:`/guides/envs_ready_made`.


.. contents::
   :local:
   :depth: 2


Top-level package
-----------------

.. automodule:: rl_environments
   :members:
   :show-inheritance:


RX200 — Simulation (Gazebo)
---------------------------

Robot envs
~~~~~~~~~~

.. automodule:: rl_environments.rx200.sim.robot_envs.rx200_robot_sim
   :members:
   :show-inheritance:


.. automodule:: rl_environments.rx200.sim.robot_envs.rx200_robot_goal_sim
   :members:
   :show-inheritance:


Vision-augmented robot envs
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: rl_environments.rx200.sim.robot_envs.rx200_robot_sim_zed2
   :members:
   :show-inheritance:


.. automodule:: rl_environments.rx200.sim.robot_envs.rx200_robot_goal_sim_zed2
   :members:
   :show-inheritance:


Reach task envs (Kinect v2 vision)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: rl_environments.rx200.sim.task_envs.reach.rx200_kinect_reach_sim
   :members:
   :show-inheritance:


.. automodule:: rl_environments.rx200.sim.task_envs.reach.rx200_kinect_reach_goal_sim
   :members:
   :show-inheritance:


Reach task envs (ZED 2 vision)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: rl_environments.rx200.sim.task_envs.reach.rx200_zed2_reach_sim
   :members:
   :show-inheritance:


.. automodule:: rl_environments.rx200.sim.task_envs.reach.rx200_zed2_reach_goal_sim
   :members:
   :show-inheritance:


RX200 — Real hardware
---------------------

Robot envs
~~~~~~~~~~

.. automodule:: rl_environments.rx200.real.robot_envs.rx200_robot_real
   :members:
   :show-inheritance:


.. automodule:: rl_environments.rx200.real.robot_envs.rx200_robot_goal_real
   :members:
   :show-inheritance:


Niryo Ned2 — Simulation
-----------------------

Robot envs
~~~~~~~~~~

.. automodule:: rl_environments.ned2.sim.robot_envs.ned2_robot_sim
   :members:
   :show-inheritance:


.. automodule:: rl_environments.ned2.sim.robot_envs.ned2_robot_goal_sim
   :members:
   :show-inheritance:


Reach task envs
~~~~~~~~~~~~~~~

.. automodule:: rl_environments.ned2.sim.task_envs.reach.ned2_reach_sim
   :members:
   :show-inheritance:


.. automodule:: rl_environments.ned2.sim.task_envs.reach.ned2_reach_goal_sim
   :members:
   :show-inheritance:


Niryo Ned2 — Real hardware
--------------------------

.. automodule:: rl_environments.ned2.real.robot_envs.ned2_robot_real
   :members:
   :show-inheritance:


.. automodule:: rl_environments.ned2.real.robot_envs.ned2_robot_goal_real
   :members:
   :show-inheritance:
