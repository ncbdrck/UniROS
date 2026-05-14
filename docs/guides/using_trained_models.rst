Using trained models
====================

Once you've trained a model with :doc:`training`, you can load the
saved ``.zip`` file and run it against any env that exposes the
same observation/action space.


Load and predict
----------------

The pattern matches Stable Baselines 3 itself, wrapped to read the
same YAML config the training script used:

.. code-block:: python

   import rospy
   import uniros as gym
   import rl_environments

   from sb3_ros_support.sac import SAC


   rospy.init_node("rx200_validate_sim")
   env = gym.make("RX200ReacherSim-v0", gazebo_gui=True)
   obs, _ = env.reset()

   # Load the trained model. ``save_path`` is the same value you
   # used when saving; the .zip extension is added automatically.
   model = SAC.load_trained_model(
       "/models/sac/trained_model_name",
       env=env,
       model_pkg="rl_training_validation",
       config_filename="rx200_reacher_sac.yaml",
   )

   # Run validation episodes
   episodes = 50
   epi_count = 0
   while epi_count < episodes:
       action, _ = model.predict(obs, deterministic=True)
       obs, reward, terminated, truncated, info = env.step(action)
       if terminated or truncated:
           epi_count += 1
           rospy.loginfo(f"Episode {epi_count} / {episodes}")
           obs, _ = env.reset()

   env.close()


Validate sim-trained models on real hardware
--------------------------------------------

The framework's value proposition: an env trained under
``MyRobotReachSim-v0`` can be validated on ``MyRobotReachReal-v0``
without retraining, as long as the action and observation spaces
match.

.. code-block:: python

   # Bring up the real robot's driver in a separate terminal first:
   #   roslaunch my_robot_bringup robot.launch

   import rospy
   import uniros as gym
   import rl_environments

   from sb3_ros_support.sac import SAC


   rospy.init_node("rx200_validate_real")

   # Same env API, different backend
   env = gym.make("RX200ReacherReal-v0")
   obs, _ = env.reset()

   model = SAC.load_trained_model(
       "/models/sac/trained_in_sim",
       env=env,
       model_pkg="rl_training_validation",
       config_filename="rx200_reacher_sac.yaml",
   )

   # Slow start — confirm the first action is sensible before
   # letting the loop run freely.
   for _ in range(3):
       action, _ = model.predict(obs, deterministic=True)
       rospy.loginfo(f"First action: {action}")
       obs, _, term, trunc, _ = env.step(action)
       if term or trunc:
           obs, _ = env.reset()

If the policy looks unsafe (joint velocities too high, target
positions outside the workspace, etc.), stop the script and:

* Tighten the action clip in the env's ``_set_action()``.
* Lower the SB3 ``action_noise`` even in validation (deterministic
  prediction should ignore noise, but double-check the YAML).
* Retrain with reward shaping that penalises large actions.


Deterministic vs stochastic prediction
--------------------------------------

``model.predict(obs, deterministic=True)`` returns the policy's
mean action — what you want for validation on hardware.

``deterministic=False`` samples from the policy's distribution.
Useful during training-time evaluation when you want stochastic
behaviour, but not when reproducing the trained policy.


Common pitfalls
---------------

* **Observation-space mismatch.** Loading a model expects the env's
  ``observation_space`` and ``action_space`` to match what was used
  at training. If you changed the obs space (e.g. added camera
  channels) you can't reuse the old model.
* **Goal-env mismatch.** A model trained on a goal env (HER) can't
  be loaded onto a non-goal env. The classes are different.
* **Config-file changes.** The YAML config you pass to
  ``load_trained_model`` must reference compatible
  ``policy_kwargs`` (architecture, normalisation). If you've
  changed the network shape, the load will fail.
* **Different gymnasium ID, same robot.** Validating a
  ``Real-v0`` model on a ``Sim-v0`` env (or vice versa) only works
  if the action/observation spaces are byte-identical. The
  framework's templates aim to keep them that way; verify before
  loading.
