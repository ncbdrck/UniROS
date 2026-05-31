Training a model
================

The environments produced by this framework are **standard
gymnasium environments** that expose the usual
``reset`` / ``step`` / ``action_space`` / ``observation_space``
surface. Any RL library that consumes those should work.
Verification status:

* **Tested**: Stable Baselines 3 via ``sb3_ros_support`` (the
  primary path used in the paper experiments and in
  ``rl_training_validation``).
* **Likely works**: plain Stable Baselines 3 without the support
  wrapper; hand-written training loops.
* **Unverified but expected to work**: CleanRL, Tianshou, RLlib,
  Tensorforce. They each inspect a few env attributes (``spec``,
  ``metadata``, ``unwrapped``, vector-env assumptions) that the
  proxy forwards correctly via ``__getattr__``, but the full
  matrix hasn't been exercised end-to-end.

``uniros.make()`` returns a proxy that behaves like ``gym.Env``
but runs the underlying env in a worker process. That's the only
framework-specific detail; everything downstream is gymnasium-
shaped.

This page shows three increasingly involved options:

1. :ref:`training-raw-sb3` — pure Stable Baselines 3 with no
   ROS-specific wrappers.
2. :ref:`training-sb3-ros-support` — the convenience layer that
   ships with this ecosystem (YAML config, ROS-aware paths,
   uniform train / save / load surface, HER ready for goal envs).
3. :ref:`training-other-frameworks` — pointers for using CleanRL,
   Tianshou, RLlib, or a custom loop.

For the dedicated joint-sim-and-real training pattern (Use Case
C from the paper), see :doc:`joint_sim_real_training`.


.. _training-raw-sb3:

Option 1 — Plain Stable Baselines 3
-----------------------------------

The simplest possible training script. No YAML, no extra wrappers,
just SB3 against a uniros-managed env.

.. code-block:: python

   #!/bin/python3
   import rospy
   from multiros.utils import gazebo_core
   import uniros as gym
   import rl_environments  # registers gym IDs

   from stable_baselines3 import SAC


   if __name__ == "__main__":
       gazebo_core.launch_gazebo(launch_roscore=True, gui=False)
       rospy.init_node("rx200_reach_train_plain_sb3")

       env = gym.make("RX200ReacherSim-v0")

       model = SAC(
           "MlpPolicy",
           env,
           learning_rate=3e-4,
           buffer_size=1_000_000,
           batch_size=256,
           tensorboard_log="./tb_logs/",
           verbose=1,
       )
       model.learn(total_timesteps=100_000)
       model.save("rx200_reach_sac")

       env.close()

This works because ``uniros.make`` returns an object that responds
to ``reset`` / ``step`` / ``close`` exactly like ``gym.Env``. SB3
doesn't know or care about ROS.


.. _training-sb3-ros-support:

Option 2 — sb3_ros_support
--------------------------

If your script already lives in a ROS package and you want
config-driven training (so swapping PPO for SAC for TD3 is a YAML
edit, not a code rewrite), :doc:`/api/sb3_ros_support` adds:

* A ``BasicModel`` base class and one subclass per algorithm —
  ``PPO``, ``A2C``, ``DDPG``, ``TD3``, ``SAC``, ``DQN``, plus their
  goal-conditioned ``*_GOAL`` variants for HER.
* YAML-driven hyperparameter loading via ``ros_load_yaml``.
* Convenient ``train`` / ``save_model`` / ``load_trained_model``
  / ``predict`` surface that wraps the underlying SB3 model.

.. code-block:: python

   #!/bin/python3
   import rospy
   from multiros.utils import gazebo_core
   import uniros as gym
   import rl_environments

   from sb3_ros_support.td3 import TD3


   if __name__ == "__main__":
       gazebo_core.launch_gazebo(launch_roscore=True, gui=False)
       rospy.init_node("rx200_reach_train_sim")

       env = gym.make("RX200ReacherSim-v0")
       env.reset()

       # YAML config lives inside the rl_training_validation package's
       # ``config/`` directory. Replace the filename for SAC, PPO, etc.
       pkg_path = "rl_training_validation"
       model = TD3(
           env,
           save_model_path="/models/td3/",
           log_path="/logs/td3/",
           model_pkg_path=pkg_path,
           config_file_pkg=pkg_path,
           config_filename="rx200_reacher_td3.yaml",
       )

       model.train()
       model.save_model()

       env.close()

Working examples live under
``rl_training_validation/src/rl_training_validation/<robot>/<task>/``
for every supported robot/task pair:

.. list-table::
   :widths: 12 18 35 35
   :header-rows: 1

   * - Robot
     - Task
     - Sim scripts
     - Real scripts
   * - RX200
     - reach / push / pnp
     - ``<task>_train_sim.py`` / ``<task>_validate_sim.py``
     - ``<task>_train_real.py`` / ``<task>_validate_real.py``
   * - Ned2
     - reach / push / pnp
     - ``<task>_train_sim.py`` / ``<task>_validate_sim.py``
     - ``<task>_train_real.py`` / ``<task>_validate_real.py``
   * - VX300S
     - reach / push / pnp
     - ``<task>_train_sim.py`` / ``<task>_validate_sim.py``
     - ``<task>_train_real.py`` / ``<task>_validate_real.py``
   * - UR5e
     - reach / push / pnp
     - ``<task>_train_sim.py`` / ``<task>_validate_sim.py``
     - ``<task>_train_real.py`` / ``<task>_validate_real.py``

Each script accepts the same set of CLI flags
(``--gazebo-gui``, ``--allow-real-robot-motion``, etc.); see
``rl_training_validation/README.md`` for the canonical inventory.

See :doc:`/api/sb3_ros_support` for the full algorithm list, and
:doc:`/api/rl_training_validation` for the working scripts.


.. _training-other-frameworks:

Option 3 — Any other gymnasium-compatible framework
---------------------------------------------------

CleanRL, Tianshou, RLlib, Tensorforce, and hand-written training
loops should all be adaptable because they consume the Gymnasium
API and that's what ``uniros.make`` produces. SB3 via
``sb3_ros_support`` is the tested path; the snippets below are
integration sketches — they haven't been exercised end-to-end on
this codebase.

**CleanRL**

CleanRL training scripts are single-file. Replace the line that
creates ``env`` with ``uniros.make``:

.. code-block:: python

   import uniros as gym
   import rl_environments

   def make_env(env_id):
       def thunk():
           env = gym.make(env_id)
           return env
       return thunk

   # ... rest of CleanRL ppo_continuous_action.py / sac_continuous_action.py
   # uses `make_env` as is.

**Tianshou**

.. code-block:: python

   import uniros as gym
   import rl_environments
   from tianshou.env import DummyVectorEnv
   from tianshou.policy import SACPolicy

   env = DummyVectorEnv([lambda: gym.make("RX200ReacherSim-v0")
                        for _ in range(4)])
   # ... continue with the standard Tianshou trainer.

**RLlib**

RLlib expects a registered env. Register a thin wrapper:

.. code-block:: python

   from ray.tune.registry import register_env
   import uniros as uniros_gym
   import rl_environments

   def _make(config):
       return uniros_gym.make(config["env_id"])

   register_env("rx200_reacher", _make)

   # algo = ppo.PPO(config={"env": "rx200_reacher",
   #                        "env_config": {"env_id": "RX200ReacherSim-v0"},
   #                        ...})

**Hand-written training loop**

.. code-block:: python

   import uniros as gym
   import rl_environments

   env = gym.make("RX200ReacherSim-v0")
   obs, _ = env.reset(seed=0)
   for step in range(100_000):
       action = your_policy(obs)
       obs, reward, term, trunc, info = env.step(action)
       your_learner.observe(obs, action, reward, term)
       if term or trunc:
           obs, _ = env.reset()

The only point where the framework's identity matters is the call
to ``uniros.make`` (which runs the env in a worker process). Once
you have the proxy in hand, treat it as a normal gymnasium env.


Configuration via YAML (sb3_ros_support)
----------------------------------------

When using ``sb3_ros_support``, hyperparameters live in a YAML file
under any ROS package you control. The working examples ship under
``rl_training_validation/config/`` and cover all four robots ×
three tasks × standard/goal variants (34 files total):

* **Reach** — SAC and TD3 (standard + goal) for every robot:
  ``<robot>_reacher_sac.yaml``, ``<robot>_reacher_sac_goal.yaml``,
  ``<robot>_reacher_td3.yaml``, ``<robot>_reacher_td3_goal.yaml``.
* **Push** — TD3 (standard + goal) for every robot:
  ``<robot>_push_td3.yaml``, ``<robot>_push_td3_goal.yaml``.
* **PnP** — TD3 (standard + goal) for every robot:
  ``<robot>_pnp_td3.yaml``, ``<robot>_pnp_td3_goal.yaml``.
* **Multi-task** — ``multi_task_td3.yaml`` / ``multi_task_td3_goal.yaml``
  for joint sim+real training (see :doc:`joint_sim_real_training`).

``<robot>`` is one of ``rx200``, ``ned2``, ``vx300s``, ``ur5e``.

A typical file:

.. code-block:: yaml

   total_timesteps: 100000
   learning_starts: 1000

   policy: "MlpPolicy"
   policy_kwargs:
     net_arch: [256, 256]
   learning_rate: 0.0003

   buffer_size: 1000000
   batch_size: 256
   gamma: 0.99
   tau: 0.005

   action_noise:
     type: "normal"
     mean: 0.0
     stddev: 0.1

   # HER block (only for *_GOAL algorithms)
   her:
     n_sampled_goal: 4
     goal_selection_strategy: "future"

Pass the filename to the algorithm wrapper's ``config_filename``;
all the keys above are read at ``train()`` time.


Logging and checkpoints
-----------------------

Whichever option you use, TensorBoard is the standard reader:

.. code-block:: bash

   tensorboard --logdir /path/to/logs/
   # then open http://localhost:6006

Saved models from ``sb3_ros_support`` are SB3 ``.zip`` files that
can be loaded back via
:func:`sb3_ros_support.core.BasicModel.load_trained_model` or
SB3's own ``Algorithm.load(...)``.

Weights & Biases (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When training through ``sb3_ros_support``, the same metrics can be
mirrored to `Weights & Biases <https://wandb.ai/>`_ for a hosted web
UI you can watch from anywhere. It is **off by default**; enable it
per config:

.. code-block:: yaml

   use_wandb: True
   wandb_params:
     project: uniros     # W&B project name
     entity:             # your W&B username/team; blank uses your default

Then install and log in once::

   pip install wandb
   wandb login

The run starts automatically with ``sync_tensorboard=True``, so every
metric SB3 already writes to TensorBoard appears in W&B too — no
per-algorithm changes. ``wandb`` is an optional dependency and is
lazily imported: if it is not installed, training logs a warning and
continues with TensorBoard only. W&B is skipped when loading a saved
model for validation.
