Quickstart
==========

This page walks you through launching a pre-built RX200 reach env
and stepping it once. It assumes you've finished :doc:`install`,
including the optional ``rl_environments`` clone and the RX200
robot drivers.


Verify the workspace
--------------------

.. code-block:: bash

   source ~/catkin_ws/devel/setup.bash
   python3 -c "import uniros, multiros, realros, rl_environments; print('OK')"

If any package fails to import, make sure the workspace was built
(``catkin build``) and sourced (``source devel/setup.bash``).


A complete first script
-----------------------

Save the following as ``rx200_quickstart.py`` and run it. It
launches a roscore + Gazebo, registers the pre-built RX200 envs,
makes a reach env, and steps it 100 times.

.. code-block:: python

   #!/usr/bin/env python3
   import rospy
   from multiros.utils import gazebo_core
   import uniros as gym               # process-per-env proxy
   import rl_environments              # registers the gymnasium env IDs

   if __name__ == "__main__":
       # Pick free ports, spawn roscore + Gazebo as detached xterms,
       # set ROS_MASTER_URI / GAZEBO_MASTER_URI so the subsequent
       # gym.make() talks to the right master.
       ros_port, gazebo_port, gazebo_proc = gazebo_core.launch_gazebo(
           launch_roscore=True,
           paused=False,
           gui=True,
       )

       rospy.init_node("rx200_quickstart")

       env = gym.make("RX200ReacherSim-v0")
       obs, info = env.reset(seed=42)
       for _ in range(100):
           action = env.action_space.sample()
           obs, reward, terminated, truncated, info = env.step(action)
           if terminated or truncated:
               obs, info = env.reset()
       env.close()

Why ``import uniros as gym`` instead of ``import gymnasium as gym``?
``uniros.make`` spawns the env inside a worker process and hands
back a proxy. Each env gets its own rospy state, so you can run
several in parallel against different rosmasters without
cross-contamination. The drop-in replacement keeps the rest of
your training code identical.


Press Ctrl+C
------------

When you're done, ``Ctrl+C`` in the terminal that started the script
tears down only the roscore and Gazebo processes this script
spawned — they're tracked in a managed-process registry and cleaned
up via a ``rospy.on_shutdown`` hook plus a SIGINT fallback. Other
ROS sessions on the same host are not affected.

If the training loop is stuck in a non-responsive C call (e.g.
``stable_baselines3.learn()``), a second ``Ctrl+C`` will terminate
the process immediately — the framework resets the SIGINT handler
to default after cleanup runs.


What's next
-----------

* :doc:`overview` — architectural picture, multiprocessing model,
  lifecycle / cleanup mechanism.
* :doc:`envs_ready_made` — what's currently available out of the
  box (robots, tasks, sim/real combinations).
* :doc:`env_creation_sim` — how to add a new simulation env.
* :doc:`env_creation_real` — how to add a new real-hardware env.
* :doc:`training` — wire your env into Stable Baselines 3 via
  ``sb3_ros_support``.
