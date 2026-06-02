Creating a simulation environment
=================================

This guide walks through adding a new Gazebo-based environment
end-to-end, from picking a starting template to registering the
gymnasium ID and running a smoke test.

If you're new to the two-layer pattern, read :doc:`env_templates`
first.


1. Pick a starting point
------------------------

* **New robot, new task** — copy both layers from the MultiROS
  templates (``MyRobotEnv.py`` + ``MyTaskEnv.py``). You'll be doing
  the most work.
* **Existing robot, new task** — copy only the task layer
  (``MyTaskEnv.py`` / ``MyTaskGoalEnv.py``) and inherit from the
  existing robot env.
* **Reach-like task** — start from ``rl_environments/src/rl_environments/
  rx200/sim/task_envs/reach/rx200_reach_sim.py`` and adapt.

Goal-conditioned tasks (suitable for HER) use the
``...GoalEnv.py`` templates and the
:class:`multiros.envs.GazeboGoalEnv.GazeboGoalEnv` base class.


2. Implement the robot env
--------------------------

The robot env extends :class:`multiros.envs.GazeboBaseEnv.GazeboBaseEnv`
(or its goal variant). The base class handles the lifecycle —
spawning the robot model in Gazebo, pausing/unpausing physics,
loading ROS controllers — so your job is to fill in:

* ``_set_init_params(options=None)`` — robot-side reset (move to home
  pose, wait for controllers, etc.).
* Optional helpers for the task layer (e.g. ``get_ee_pose()``,
  ``move_to_joint_target(joint_array)``).

Spawning is configured via the base class's ``__init__`` parameters.
A typical robot env constructor looks like::

   class MyRobotSim(GazeboBaseEnv):
       def __init__(self, **kwargs):
           super().__init__(
               robot_name="my_robot",
               robot_model_xml=load_urdf("my_robot_description"),
               robot_pos_x=0.0,
               robot_pos_y=0.0,
               robot_pos_z=0.0,
               robot_ori_w=1.0,        # NOT 0.0 — see env_templates
               ros_controllers_list=["my_arm_controller", ...],
               **kwargs,
           )


3. Implement the task env
-------------------------

The task env extends your robot env and defines the gymnasium
contract. Required overrides:

* ``_get_observation()`` — return the observation array (or dict for goal envs).
* ``_set_action(action)`` — apply the action to the robot.
* ``_compute_terminated(info=None)`` — terminal-condition check
  (success / failure that should end the episode).
* ``_compute_truncated(info=None)`` — wall-clock / step-limit
  truncation; usually leave this to the ``TimeLimit`` wrapper and
  return ``False`` here.
* ``compute_reward(achieved_goal, desired_goal, info)`` (note: no
  leading underscore — this is the gymnasium-robotics ``GoalEnv``
  contract used by HER) for goal envs, or ``_get_reward(info=None)``
  for non-goal envs.
* ``_set_init_params(options=None)`` — task-side reset (e.g.
  randomise target, reset object positions). Same name as the
  robot-side hook above; override at whichever layer is more
  natural for the task and call ``super()`` if you need both to run.

The base class also wants you to declare ``observation_space`` and
``action_space`` in ``__init__``. Use ``gymnasium.spaces.Box`` (with
``seed=`` for reproducibility) or ``Dict`` for goal envs.

For reward design tips, examine
``rl_environments/src/rl_environments/rx200/sim/task_envs/reach/
rx200_reach_sim.py`` — it shows distance-to-target reward with
optional sparse/dense modes.


4. Register with gymnasium
--------------------------

In your package's ``__init__.py``:

.. code-block:: python

   from gymnasium.envs.registration import register

   register(
       id="MyRobotReachSim-v0",
       entry_point="my_pkg.task_envs.my_robot_reach_sim:MyRobotReachSim",
       max_episode_steps=200,
   )


5. Smoke test
-------------

Without involving SB3, confirm the env runs end-to-end:

.. code-block:: python

   import rospy
   from multiros.utils import gazebo_core
   import uniros as gym
   import my_pkg                   # triggers gymnasium.register

   gazebo_core.launch_gazebo(launch_roscore=True, gui=True)
   rospy.init_node("smoke_test")

   env = gym.make("MyRobotReachSim-v0")
   obs, info = env.reset(seed=0)
   for _ in range(100):
       obs, reward, term, trunc, info = env.step(env.action_space.sample())
       if term or trunc:
           obs, info = env.reset()
   env.close()

If the env runs cleanly here, plug it into a training script — see
:doc:`training`.


Configuration via YAML
----------------------

Production envs typically read their hyperparameters (timesteps,
reward coefficients, action limits) from a YAML file under
``config/<env>_config.yaml``. Look at
``rl_environments/config/rx200_reach_task_config.yaml`` for a
template. Loading the file:

.. code-block:: python

   from multiros.utils.ros_common import ros_load_yaml
   ros_load_yaml(pkg_name="my_pkg", file_name="my_task_config.yaml", ns="/")
   self.reward_coefficient = rospy.get_param("my_task/reward_coefficient")


Common pitfalls
---------------

* **Gazebo physics multiplier**. If you set
  ``gazebo_update_rate_multiplier`` above 1.0 in your config, the
  simulator runs faster than wall-clock — which breaks any agent
  loop paced by wall time. Keep it at ``1.0`` unless you've
  consciously redesigned the timing.
* **Quaternion default**. ``robot_ori_w=0.0`` is a zero quaternion;
  use ``1.0`` for identity.
* **Seed leakage**. Use ``self.np_random`` (populated by the base
  class via ``super().reset(seed=seed)``), not ``np.random``.
* **Stuck on reset**. If reset hangs forever, check that your
  ROS controllers actually report ``running`` and that
  ``wait_for_service`` calls have timeouts.
