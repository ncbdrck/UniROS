MultiROS API reference
======================

Gazebo-simulation environments built on the shared UniROS proxy and
utilities. Use this package when you want to train RL agents
against simulated robots.


.. contents::
   :local:
   :depth: 2


Top-level package
-----------------

.. automodule:: multiros
   :members:
   :show-inheritance:


Gym proxy (re-export)
---------------------

.. automodule:: multiros.core
   :members:
   :show-inheritance:
   :noindex:

The ``MultirosGym`` class in this module is an alias for
:class:`uniros._proxy.GymProxy` — see the UniROS API page for the
full method reference.


Gazebo lifecycle
----------------

.. automodule:: multiros.utils.gazebo_core
   :members:
   :show-inheritance:


Gazebo models
~~~~~~~~~~~~~

.. automodule:: multiros.utils.gazebo_models
   :members:
   :show-inheritance:


Gazebo physics
~~~~~~~~~~~~~~

.. automodule:: multiros.utils.gazebo_physics
   :members:
   :show-inheritance:


ROS helpers
-----------

ROS common
~~~~~~~~~~

.. automodule:: multiros.utils.ros_common
   :members:
   :show-inheritance:


ROS controllers (re-export)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: multiros.utils.ros_controllers
   :no-members:

Re-export of :mod:`uniros.utils.ros_controllers`. See the UniROS
API page for the full helper reference.


ROS markers (re-export)
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: multiros.utils.ros_markers
   :no-members:

Re-export of :mod:`uniros.utils.ros_markers`.


ROS kinematics (re-export)
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: multiros.utils.ros_kinematics
   :no-members:

Re-export of :mod:`uniros.utils.ros_kinematics`.


MoveIt integration
------------------

.. automodule:: multiros.utils.moveit_multiros
   :members:
   :show-inheritance:


Base envs
---------

GazeboBaseEnv
~~~~~~~~~~~~~

.. automodule:: multiros.envs.GazeboBaseEnv
   :members:
   :show-inheritance:


GazeboGoalEnv
~~~~~~~~~~~~~

.. automodule:: multiros.envs.GazeboGoalEnv
   :members:
   :show-inheritance:


Wrappers
--------

.. automodule:: multiros.wrappers.normalize_action_wrapper
   :members:
   :show-inheritance:


.. automodule:: multiros.wrappers.normalize_obs_wrapper
   :members:
   :show-inheritance:


.. automodule:: multiros.wrappers.time_limit_wrapper
   :members:
   :show-inheritance:
