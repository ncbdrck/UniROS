Training a model
================

This page covers wiring a gym env into Stable Baselines 3 via
:doc:`/api/sb3_ros_support`. The package adapts SB3 for ROS-based
training scripts: each algorithm subclass exposes a uniform
``train`` / ``validate`` / ``save`` / ``load`` surface, so swapping
PPO for SAC for TD3 is a configuration edit, not a code rewrite.


Anatomy of a training script
----------------------------

A typical training script does five things:

1. Launch the env infrastructure (Gazebo for sim, or attach to a
   robot driver for real).
2. ``import uniros as gym`` and ``gym.make`` your env.
3. Instantiate the algorithm wrapper from ``sb3_ros_support``
   pointing at a YAML config file.
4. Call ``.train()`` then ``.save_model()``.
5. (Optional) Validate the trained model on the same env or its
   real-world counterpart.

A minimal example for the RX200 reach env:

.. code-block:: python

   #!/bin/python3
   import rospy
   from multiros.utils import gazebo_core
   import uniros as gym
   import rl_environments                     # registers the gym IDs

   from sb3_ros_support.sac import SAC


   if __name__ == "__main__":
       # 1. Bring up Gazebo + roscore
       gazebo_core.launch_gazebo(launch_roscore=True, gui=False)
       rospy.init_node("rx200_reach_train_sim")

       # 2. Make the env via uniros so it runs in a worker process
       env = gym.make("RX200ReacherSim-v0")
       env.reset()

       # 3. Instantiate the SAC wrapper. The config_filename points
       #    to a YAML file inside the rl_environments package.
       model = SAC(
           env,
           save_model_path="/models/sac/",
           log_path="/logs/sac/",
           model_pkg_path="rl_environments",
           config_file_pkg="rl_environments",
           config_filename="sac.yaml",
       )

       # 4. Train and save
       model.train()
       model.save_model()

       env.close()


Algorithm wrappers
------------------

``sb3_ros_support`` exposes one class per SB3 algorithm. Each
subclasses :class:`sb3_ros_support.core.BasicModel`:

**Non-goal algorithms** (use with regular ``gym.Env``)

* :class:`sb3_ros_support.ppo.PPO`
* :class:`sb3_ros_support.a2c.A2C`
* :class:`sb3_ros_support.ddpg.DDPG`
* :class:`sb3_ros_support.td3.TD3`
* :class:`sb3_ros_support.sac.SAC`
* :class:`sb3_ros_support.dqn.DQN`

**Goal-conditioned algorithms** (use with goal envs;
HER replay buffer enabled in config)

* :class:`sb3_ros_support.ddpg_goal.DDPG_GOAL`
* :class:`sb3_ros_support.td3_goal.TD3_GOAL`
* :class:`sb3_ros_support.sac_goal.SAC_GOAL`
* :class:`sb3_ros_support.dqn_goal.DQN_GOAL`

Switching between them requires changing one import and one class
name; the rest of the script stays the same. The hyperparameters
move into the YAML file.


YAML configuration
------------------

Every algorithm reads hyperparameters from a YAML file. Look in
``rl_environments/config/`` for working examples (e.g.
``sac.yaml``, ``td3.yaml``, ``sac_goal.yaml``). Typical contents:

.. code-block:: yaml

   # ---- training schedule ----
   total_timesteps: 100000
   learning_starts: 1000

   # ---- policy ----
   policy: "MlpPolicy"
   policy_kwargs:
     net_arch: [256, 256]
   learning_rate: 0.0003

   # ---- buffer / batch ----
   buffer_size: 1000000
   batch_size: 256
   gamma: 0.99
   tau: 0.005

   # ---- exploration / noise ----
   action_noise:
     type: "normal"
     mean: 0.0
     stddev: 0.1

   # ---- HER (only for *_GOAL algorithms) ----
   her:
     n_sampled_goal: 4
     goal_selection_strategy: "future"

The exact keys recognised depend on the algorithm; see
:class:`sb3_ros_support.core.BasicModel.__init__` and the
algorithm-specific subclass.


Working training scripts
------------------------

In ``rl_training_validation/src/rl_training_validation/``:

* ``rx200/reach/rx200_reach_train_sim.py`` — RX200 sim reach training.
* ``rx200/reach/rx200_reach_validate_sim.py`` — load a trained
  RX200 model and run validation episodes.
* ``rx200/reach/rx200_reach_train_real.py`` — same task, real hardware.
* ``rx200/reach/rx200_reach_validate_real.py`` — real-world validation.
* ``multi_task_learning/multi_train_sim.py`` — joint training across
  multiple task envs in one process.

Copy any of these as the starting point for a new training script;
swap the env ID, config file, and algorithm class.


Sim-to-real and joint training
------------------------------

The framework supports three common workflows:

1. **Sim-only** — train under ``...Sim-v0``, save the model. Easy
   iteration; no hardware risk.
2. **Sim-then-real validation** — train in sim, then load the
   saved model against the matching ``...Real-v0`` env to validate
   without further updates. See :doc:`using_trained_models`.
3. **Joint sim+real training** — run two envs (one sim, one real)
   in the same training loop so the policy receives transitions
   from both worlds. This needs a ``MultiTaskEnv`` wrapper
   (:mod:`rl_training_validation.utils.multi_task_env`) and a
   training script that holds both envs open.


Logging and checkpoints
-----------------------

SB3 writes TensorBoard logs to ``log_path`` and periodic
checkpoints to ``save_model_path``. To watch training live:

.. code-block:: bash

   tensorboard --logdir /path/to/logs/sac/

Final model is saved by ``model.save_model()`` as a ``.zip`` file
that :func:`sb3_ros_support.core.BasicModel.load_trained_model`
can later read back.
