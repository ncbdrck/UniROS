Joint sim + real training
=========================

One of the three use cases laid out in the UniROS paper
(`Kapukotuwa et al., 2025 <https://www.mdpi.com/1424-8220/25/18/5679>`_,
Section IX.C) is **simultaneously learning a single policy in both
simulation and the real world**. The agent sees transitions from
both domains in the same training loop, and the resulting policy
is designed to generalise across the reality gap rather than
relying on domain randomisation or post-hoc transfer.

This page walks through the pattern.


The idea in one paragraph
-------------------------

You hold two environment instances open at once — one Gazebo sim
env (MultiROS), one real-hardware env (RealROS) — with **the same
observation and action spaces**. At each episode you pick one of
them, run the episode end-to-end (sampling actions from the same
policy network, recording transitions to the same replay buffer),
then update the actor and critic networks from a mixed batch.
Over time the policy is pushed to be competent in both domains.


Algorithm (TD3 / TD3+HER, from the paper)
-----------------------------------------

The reference algorithm from the paper (slightly paraphrased):

.. code-block:: text

   Initialise the TD3 (or TD3+HER) agent.
   Initialise replay buffer R (HER for goal envs).
   Initialise an array A of real and sim environments.

   for episode = 1 to M:
       Sample an environment instance I in A      # sim or real
       Sample a goal g_t and initial state s_0
       for step = 1 to T - 1:
           a_t ~ pi(s_t) + exploration noise
           Execute a_t on I -> (r_t, s_{t+1}, done_t)
           Add (s_t, a_t, r_t, s_{t+1}, done_t) to R
       if HER:
           Augment R with pseudo-goals from the just-finished episode
       Update actor + critic from samples in R

The key observation: the sampling step ``I in A`` is the only
place the loop knows or cares which domain it's running in. The
policy, the replay buffer, and the learning update are
domain-agnostic.


The wrapper that makes this work
--------------------------------

``rl_training_validation`` ships two thin wrappers that take a
list of gym IDs and an environment-args list, build the list of
sub-envs, and round-robin (or random-sample) between them on each
``reset()``:

* :class:`rl_training_validation.utils.multi_task_env.MultiTaskEnv`
  for non-goal envs (vanilla observation space).
* :class:`rl_training_validation.utils.multi_task_goal_env.MultiTaskGoalEnv`
  for goal-conditioned envs (HER-ready).

From a training-script perspective both look like a single
``gym.Env`` / ``GoalEnv``. The wrapper:

* Picks which sub-env runs the next episode (seeded; reproducible).
* Pads the observation and action arrays to the per-env maxima
  if the sub-envs have different dimensionalities.
* Stamps ``info["task_id"]`` so the replay buffer and reward
  recomputation know which sub-env produced each transition (this
  matters for HER, which needs to call the right sub-env's
  ``compute_reward``).


Process topology
----------------

The thing that makes joint sim+real training operationally non-
trivial is that you've got **two ROS masters running at once**:
one for the Gazebo simulator and one for the real robot's driver.
The framework keeps these straight via separate roscores and
distinct ``ROS_MASTER_URI`` values:

.. code-block:: text

    +-----------------------+         +-------------------------------+
    | training script       |         | real robot driver             |
    | (your Python process) |         | (its own terminal, e.g.       |
    |                       |         |  ``roslaunch rx200 ...``)     |
    +-----------------------+         +-------------------------------+
                |                                  |
                |                                  |
                v                                  v
     +-------------------+              +-------------------------+
     | sim roscore       |              | real-robot roscore      |
     | + Gazebo          |              | (started by the driver) |
     | spawned by        |              |                         |
     | launch_gazebo()   |              |                         |
     |                   |              |                         |
     | ROS_MASTER_URI =  |              | ROS_MASTER_URI =        |
     |  http://localhost |              |  http://localhost:11311 |
     |   :<sim_port>     |              |  (or remote IP for      |
     |                   |              |   multi-device mode)    |
     +-------------------+              +-------------------------+

What you need to do operationally:

* **Terminal 1**: launch the real robot's ROS driver. By default
  this uses ``ROS_MASTER_URI=http://localhost:11311``.
* **Terminal 2**: run the training script. It calls
  ``launch_gazebo()`` which picks free ports for the simulator's
  roscore + Gazebo, separate from 11311.
* The sim env (``RX200ReacherSim-v0``) connects to the
  framework-spawned simulator roscore. The real env
  (``RX200ReacherReal-v0``) connects to the driver's roscore on
  11311. UniROS runs each env in its own worker process, so
  there's no ``ROS_MASTER_URI`` cross-contamination.
* For **remote** robots (driver running on a different machine):
  use RealROS's multi-device mode. See
  :func:`realros.utils.ros_common.change_ros_master_multi_device`.


Minimal example — TD3 + sim + real
----------------------------------

The example below trains a single TD3 agent on transitions from
both ``RX200ReacherSim-v0`` (Gazebo) and ``RX200ReacherReal-v0``
(physical robot).

.. code-block:: python

   #!/bin/python3
   import rospy
   from multiros.utils import gazebo_core
   import uniros as gym
   import rl_environments

   from rl_training_validation.utils.multi_task_env import MultiTaskEnv
   from sb3_ros_support.td3 import TD3


   if __name__ == "__main__":
       # Bring up the simulator (Gazebo). The real robot's driver
       # must already be running in a separate terminal.
       gazebo_core.launch_gazebo(launch_roscore=True, gui=False)
       rospy.init_node("rx200_reach_train_sim_and_real")

       # The wrapper holds both envs open and samples between them.
       env = MultiTaskEnv(
           env_list=["RX200ReacherSim-v0", "RX200ReacherReal-v0"],
           env_args_list=[
               {"gazebo_gui": False},
               {},
           ],
       )

       # YAML config lives in rl_training_validation/config/. Use
       # multi_task_td3.yaml for joint sim+real (covers both envs).
       pkg_path = "rl_training_validation"
       model = TD3(
           env,
           save_model_path="/models/td3_sim_real/",
           log_path="/logs/td3_sim_real/",
           model_pkg_path=pkg_path,
           config_file_pkg=pkg_path,
           config_filename="multi_task_td3.yaml",
       )

       model.train()
       model.save_model()

       env.close()


Goal-conditioned (TD3 + HER) variant
------------------------------------

For HER you need :class:`MultiTaskGoalEnv` so the wrapper routes
``compute_reward`` to the originating sub-env via ``info["task_id"]``.

.. code-block:: python

   from rl_training_validation.utils.multi_task_goal_env import MultiTaskGoalEnv
   from sb3_ros_support.td3_goal import TD3_GOAL


   env = MultiTaskGoalEnv(
       env_list=["RX200ReacherGoalSim-v0", "RX200ReacherGoalReal-v0"],
       env_args_list=[
           {"gazebo_gui": False, "reward_type": "sparse"},
           {"reward_type": "sparse"},
       ],
   )

   pkg_path = "rl_training_validation"
   model = TD3_GOAL(
       env,
       save_model_path="/models/td3_her_sim_real/",
       log_path="/logs/td3_her_sim_real/",
       model_pkg_path=pkg_path,
       config_file_pkg=pkg_path,
       config_filename="multi_task_td3_goal.yaml",
   )

   model.train()
   model.save_model()


When to use this vs. sim-only or real-only training
---------------------------------------------------

The paper's three use cases give clear guidance:

.. list-table::
   :widths: 26 24 50
   :header-rows: 1

   * - Use case
     - When to pick it
     - Trade-off
   * - **Real-world only**
     - Small workspace, safe action space, low sample cost.
     - Slowest training; every episode is a real episode.
   * - **Sim → real transfer**
     - You have a high-fidelity sim model; reality-gap is small.
     - Zero-shot transfer may fail if the sim and real dynamics
       differ enough.
   * - **Joint sim + real**
     - You want a single generalised policy and you can afford to
       run a real robot alongside the simulator.
     - Slower than sim-only because every k-th episode is real.
       Returns a policy that's competent across both domains by
       construction.

The paper's experiment on the RX200 Reach task shows that joint
sim+real reaches the same near-optimal policy as sim-only or
real-only training, but the result is *one* policy you can deploy
to either domain without further tuning.


Tuning notes from the paper
---------------------------

Empirically validated on the RX200 Reach task (Section VIII of the
paper):

* **Action cycle time of ~800 ms** worked best. Shorter (100 ms)
  pushed the agent to learn against rapidly-changing observations;
  longer (1600 ms) under-sampled the dynamics.
* **Environment loop rate of 10 Hz** matched the RX200's hardware
  control loop. Match this to your robot's ``joint_state_controller``
  publish rate to avoid the agent observing stale state.
* **TD3 for standard envs, TD3+HER for goal-conditioned envs.**
  Both converged within 10k steps for non-goal envs and 30k steps
  for goal envs.
* **Sparse vs dense rewards.** Sparse rewards learn at roughly the
  same rate as dense for the Reach task and produce more
  generalisable policies, but dense rewards converge faster — pick
  based on whether you can hand-design a dense signal cleanly.


Safety checklist
----------------

Joint training touches real hardware on most episodes. Before
launching:

* Both envs expose the same action and observation spaces. Mismatches
  will be caught by the wrapper's padding, but a policy trained on
  padded zeros will not transfer well.
* Action limits in the real env are at least as strict as in sim.
  A policy that's safe in sim is not automatically safe on hardware.
* Episode termination triggers correctly in both envs (collision,
  joint-limit violation, time limit).
* The Ctrl+C cleanup hooks tear down only the resources this
  script spawned (Gazebo + roscore + the script's own worker
  processes). The real robot's driver in the other terminal is
  unaffected and should be stopped manually when you're done.
* You can reach the e-stop while training.
