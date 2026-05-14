Creating a real-hardware environment
====================================

RealROS environments follow the same two-layer **Robot env → Task
env** pattern as MultiROS sim envs, but they talk to a physical
robot via the manufacturer's ROS driver (and typically MoveIt)
instead of Gazebo.

If you haven't built a sim env yet, read :doc:`env_creation_sim`
first — most of the task-layer reasoning carries over.


Differences from sim
--------------------

* **No Gazebo lifecycle.** No spawn / despawn / pause / unpause.
  The robot is the robot — you initialise its driver and assume
  it's running.
* **MoveIt is the usual control path.** Joint-space commands and
  cartesian goals are typically issued through MoveIt
  ``MoveGroupCommander`` rather than direct controller publishers.
* **No simulation reset.** "Reset" must be implemented as a safe
  motion to a home pose. Don't randomise initial joint positions
  without checking joint limits and collision space.
* **Wall-clock paced.** Real hardware runs at real time. Avoid any
  per-step ``time.sleep`` patterns that assume simulated time.
* **Real consequences.** Failed actions actually crash the robot.
  Test in sim first; smoke-test slowly on hardware.


1. Pick a starting point
------------------------

Templates live in ``realros/src/realros/templates/``:

* ``robot_envs/MyRealRobotEnv.py``
* ``robot_envs/MyRealRobotGoalEnv.py``
* ``task_envs/MyRealTaskEnv.py``
* ``task_envs/MyRealTaskGoalEnv.py``

Or — if you have a working sim env for the same robot/task —
**start from your sim env** and replace the Gazebo-specific bits
with MoveIt / direct-driver equivalents. The action-space and
reward function should be near-identical, which is the point of
the framework.


2. Implement the robot env
--------------------------

Extends :class:`realros.envs.RealBaseEnv.RealBaseEnv` (or its goal
variant). Required:

* ``_set_episode_init_params()`` — move to a home pose, reset
  gripper, etc.
* Helpers the task env will call: ``get_joint_positions()``,
  ``move_to_joint_target(...)``, ``move_to_pose(...)``.

Bring up the manufacturer's driver outside the env (via
``roslaunch``). The env attaches to existing ROS topics; it does
not spawn the driver process.


3. Implement the task env
-------------------------

Same gymnasium contract as the sim version:

* ``observation_space`` / ``action_space`` defined in ``__init__``.
* ``_get_obs()``, ``_set_action(action)``,
  ``_check_if_done()``, ``_compute_reward(...)``.
* ``_set_init_pose()`` for any task-side reset (e.g. resample target).

Keep the same Gymnasium ID conventions you'd use in sim, but with a
``Real`` suffix:

.. code-block:: python

   register(
       id="MyRobotReachReal-v0",
       entry_point="my_pkg.task_envs.my_robot_reach_real:MyRobotReachReal",
       max_episode_steps=200,
   )


4. Bring up the robot, then launch the env
------------------------------------------

In one terminal:

.. code-block:: bash

   roslaunch my_robot_bringup robot.launch

In another:

.. code-block:: python

   import rospy
   import uniros as gym
   import my_pkg

   rospy.init_node("real_smoke_test")
   env = gym.make("MyRobotReachReal-v0")
   obs, info = env.reset(seed=0)
   for _ in range(5):
       obs, reward, term, trunc, info = env.step(env.action_space.sample())
       if term or trunc:
           obs, info = env.reset()
   env.close()

Start with a tiny number of steps and a hand near the e-stop.


Sim-to-real transfer
--------------------

The framework is designed so a model trained in simulation can be
validated on the matching real env with the *same* action/observation
spaces. The recommended workflow:

1. Train under ``...Sim-v0`` until you're happy with the policy.
2. Save the model.
3. Load it against ``...Real-v0`` and run validation (no training
   updates):

   .. code-block:: python

      model = SAC.load_trained_model(
          save_path + "trained_model_name",
          env=real_env,
          ...
      )

See :doc:`using_trained_models` for the full pattern, and
:doc:`training` for joint sim+real training (a single agent updating
on transitions from both environments concurrently).


Safety checklist
----------------

Before clicking "run" on hardware:

* The action space cannot command joint positions outside the
  robot's limits.
* ``_compute_reward`` doesn't have a code path that incentivises
  smashing into the table.
* Episode termination triggers reliably (collision, time limit,
  joint-limit violation).
* You can stop the script with Ctrl+C — the framework's cleanup
  hooks tear down the roscore and the script process gracefully.
* The e-stop is reachable.
