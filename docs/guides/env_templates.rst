Environment templates
=====================

Both MultiROS and RealROS ship template files you can copy as the
starting point for a new environment. Each follows the two-layer
**Robot env → Task env** pattern that the framework expects.


The two-layer pattern
---------------------

Reinforcement-learning environments are split into two responsibilities:

**Robot env** — the layer that knows about the *robot*.

* What controllers it exposes (joint position, joint velocity,
  end-effector pose).
* How to read its joint states / sensors.
* How to wait for it to be ready.

This layer is reusable across tasks: the same robot env can back a
reach task, a push task, a pick-and-place task.

**Task env** — the layer that knows about the *task*.

* The gymnasium ``observation_space`` and ``action_space``.
* The reward function.
* When an episode terminates.
* What "reset to a sensible starting state" means for *this* task.

It composes the robot env (via inheritance) and adds task-specific
behaviour on top.

Base classes that wire this together live in the framework:

* :class:`multiros.envs.GazeboBaseEnv.GazeboBaseEnv`
* :class:`multiros.envs.GazeboGoalEnv.GazeboGoalEnv`
* :class:`realros.envs.RealBaseEnv.RealBaseEnv`
* :class:`realros.envs.RealGoalEnv.RealGoalEnv`


Template files
--------------


MultiROS (simulation)
~~~~~~~~~~~~~~~~~~~~~

Located at ``multiros/src/multiros/templates/``:

* ``robot_envs/MyRobotEnv.py`` — non-goal robot env template.
* ``robot_envs/MyRobotGoalEnv.py`` — goal-conditioned robot env.
* ``task_envs/MyTaskEnv.py`` — non-goal task env.
* ``task_envs/MyTaskGoalEnv.py`` — goal-conditioned task env (use
  with HER algorithms via ``sb3_ros_support``).


RealROS (real hardware)
~~~~~~~~~~~~~~~~~~~~~~~

Located at ``realros/src/realros/templates/``:

* ``robot_envs/MyRealRobotEnv.py``
* ``robot_envs/MyRealRobotGoalEnv.py``
* ``task_envs/MyRealTaskEnv.py``
* ``task_envs/MyRealTaskGoalEnv.py``


Recommended workflow
--------------------

1. **Pick the layer.** Start from a robot env if you're adding a
   new robot; start from a task env if you're adding a new task on
   an existing robot.
2. **Copy, don't symlink.** Templates evolve over time; you want
   a snapshot you can edit freely.
3. **Rename the class.** Match the file name to keep imports tidy.
4. **Fill in the abstract methods.** The template comments mark the
   methods you must implement. Each base class documents what each
   hook is expected to do.
5. **Register with gymnasium.** In your package's ``__init__.py``:

   .. code-block:: python

      from gymnasium.envs.registration import register

      register(
          id="MyTask-v0",
          entry_point="my_pkg.task_envs.MyTaskEnv:MyTask",
          max_episode_steps=1000,
      )

6. **Test under :mod:`uniros`.** Use ``import uniros as gym`` for
   the multiprocessing proxy so each env runs in its own worker.

For concrete examples of the pattern in production, look under
``rl_environments/src/rl_environments/rx200/`` — the working RX200
reach environment is built from the same templates.


Common pitfalls
---------------

* **Quaternion default**. The base envs default ``robot_ori_w=1.0``
  (identity orientation). Don't pass ``0.0`` — that's a zero
  quaternion which Gazebo will normalise but is non-portable across
  physics engines.
* **Seeded RNG**. Use ``self.np_random`` (populated by
  ``super().reset(seed=seed)``) for any random sampling. Don't use
  the global ``np.random`` — that's not seedable from the env API
  and breaks reproducibility.
* **MoveIt timeouts**. ``rospy.wait_for_service`` calls in the
  framework already have 30 s timeouts (see
  :mod:`uniros.utils.ros_controllers`). If you add your own service
  calls in a task env, follow the same pattern.
