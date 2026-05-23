rl_environments API reference
=============================

Pre-built ``gymnasium`` environments for the robots and tasks the
ecosystem currently supports. The package is organised as
``rl_environments/{robot}/{sim,real}/{robot_envs,task_envs}/...``.

For the user-facing list of working environments see
:doc:`/envs/index`.

.. note::

   This page covers the robot envs and reach task envs across all
   four supported robots. The push and pick-and-place task-env
   modules are intentionally omitted while their docstrings are
   tidied up — they're registered and importable; only the
   API-reference rendering is deferred. See :doc:`/envs/index` for
   the user-facing env reference, which does cover push and PnP.


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


Reach task envs
~~~~~~~~~~~~~~~

.. automodule:: rl_environments.rx200.real.task_envs.reach.rx200_reach_real
   :members:
   :show-inheritance:


.. automodule:: rl_environments.rx200.real.task_envs.reach.rx200_reach_goal_real
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

Robot envs
~~~~~~~~~~

.. automodule:: rl_environments.ned2.real.robot_envs.ned2_robot_real
   :members:
   :show-inheritance:


.. automodule:: rl_environments.ned2.real.robot_envs.ned2_robot_goal_real
   :members:
   :show-inheritance:


Reach task envs
~~~~~~~~~~~~~~~

.. automodule:: rl_environments.ned2.real.task_envs.reach.ned2_reach_real
   :members:
   :show-inheritance:


.. automodule:: rl_environments.ned2.real.task_envs.reach.ned2_reach_goal_real
   :members:
   :show-inheritance:


Trossen VX300S — Simulation
---------------------------

Robot envs
~~~~~~~~~~

.. automodule:: rl_environments.vx300s.sim.robot_envs.vx300s_robot_sim
   :members:
   :show-inheritance:


.. automodule:: rl_environments.vx300s.sim.robot_envs.vx300s_robot_goal_sim
   :members:
   :show-inheritance:


Reach task envs
~~~~~~~~~~~~~~~

.. automodule:: rl_environments.vx300s.sim.task_envs.reach.vx300s_reach_sim
   :members:
   :show-inheritance:


.. automodule:: rl_environments.vx300s.sim.task_envs.reach.vx300s_reach_goal_sim
   :members:
   :show-inheritance:


Trossen VX300S — Real hardware
------------------------------

Robot envs
~~~~~~~~~~

.. automodule:: rl_environments.vx300s.real.robot_envs.vx300s_robot_real
   :members:
   :show-inheritance:


.. automodule:: rl_environments.vx300s.real.robot_envs.vx300s_robot_goal_real
   :members:
   :show-inheritance:


Reach task envs
~~~~~~~~~~~~~~~

.. automodule:: rl_environments.vx300s.real.task_envs.reach.vx300s_reach_real
   :members:
   :show-inheritance:


.. automodule:: rl_environments.vx300s.real.task_envs.reach.vx300s_reach_goal_real
   :members:
   :show-inheritance:


Universal Robots UR5e — Simulation
----------------------------------

Robot envs
~~~~~~~~~~

.. automodule:: rl_environments.ur5e.sim.robot_envs.ur5e_robot_sim
   :members:
   :show-inheritance:


.. automodule:: rl_environments.ur5e.sim.robot_envs.ur5e_robot_goal_sim
   :members:
   :show-inheritance:


Reach task envs
~~~~~~~~~~~~~~~

.. automodule:: rl_environments.ur5e.sim.task_envs.reach.ur5e_reach_sim
   :members:
   :show-inheritance:


.. automodule:: rl_environments.ur5e.sim.task_envs.reach.ur5e_reach_goal_sim
   :members:
   :show-inheritance:


Universal Robots UR5e — Real hardware
-------------------------------------

Robot envs
~~~~~~~~~~

.. automodule:: rl_environments.ur5e.real.robot_envs.ur5e_robot_real
   :members:
   :show-inheritance:


.. automodule:: rl_environments.ur5e.real.robot_envs.ur5e_robot_goal_real
   :members:
   :show-inheritance:


Reach task envs
~~~~~~~~~~~~~~~

.. automodule:: rl_environments.ur5e.real.task_envs.reach.ur5e_reach_real
   :members:
   :show-inheritance:


.. automodule:: rl_environments.ur5e.real.task_envs.reach.ur5e_reach_goal_real
   :members:
   :show-inheritance:
