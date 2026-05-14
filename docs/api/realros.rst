RealROS API reference
=====================

Real-hardware environments built on the shared UniROS proxy and
utilities. Same gym API as MultiROS, talks to physical robot
drivers (typically via MoveIt) instead of Gazebo.


.. contents::
   :local:
   :depth: 2


Top-level package
-----------------

.. automodule:: realros
   :members:
   :show-inheritance:


Gym proxy (re-export)
---------------------

.. automodule:: realros.core
   :members:
   :show-inheritance:
   :noindex:

The ``RealrosGym`` class in this module is an alias for
:class:`uniros._proxy.GymProxy` — see the UniROS API page for the
full method reference.


ROS helpers
-----------

ROS common
~~~~~~~~~~

.. automodule:: realros.utils.ros_common
   :members:
   :show-inheritance:


ROS controllers (re-export)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: realros.utils.ros_controllers
   :no-members:

Re-export of :mod:`uniros.utils.ros_controllers`. See the UniROS
API page for the full helper reference.


ROS markers (re-export)
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: realros.utils.ros_markers
   :no-members:

Re-export of :mod:`uniros.utils.ros_markers`.


ROS kinematics (re-export)
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: realros.utils.ros_kinematics
   :no-members:

Re-export of :mod:`uniros.utils.ros_kinematics`.


MoveIt integration
------------------

.. automodule:: realros.utils.moveit_realros
   :members:
   :show-inheritance:


Base envs
---------

RealBaseEnv
~~~~~~~~~~~

.. automodule:: realros.envs.RealBaseEnv
   :members:
   :show-inheritance:


RealGoalEnv
~~~~~~~~~~~

.. automodule:: realros.envs.RealGoalEnv
   :members:
   :show-inheritance:


Wrappers
--------

.. automodule:: realros.wrappers.normalize_action_wrapper
   :members:
   :show-inheritance:


.. automodule:: realros.wrappers.normalize_obs_wrapper
   :members:
   :show-inheritance:


.. automodule:: realros.wrappers.time_limit_wrapper
   :members:
   :show-inheritance:
