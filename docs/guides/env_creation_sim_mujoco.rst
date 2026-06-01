Creating a simulation environment (MuJoCo)
==========================================

.. admonition:: Available (experimental) — not yet merged
   :class: warning

   The MuJoCo backend is **available but experimental**, on the
   MultiROS branch ``feature/mujoco-backend``; it is usable today but
   not yet merged into a stable release, and APIs and defaults may
   change. For the stable Gazebo workflow see
   :doc:`env_creation_sim`; for the backend overview see
   :doc:`mujoco_backend`.

This guide walks through adding a new MuJoCo-based environment
end-to-end. It mirrors the Gazebo guide (:doc:`env_creation_sim`) —
the two-layer robot-env / task-env pattern is identical — and focuses
on the pieces that are specific to MuJoCo: the MJCF scene, stripping
URDF transmissions the model does not have, and (for manipulation
tasks) objects as free-joint bodies.

The worked example throughout is the ``vx300s_mujoco_envs`` package
(`github.com/ncbdrck/vx300s_mujoco_envs
<https://github.com/ncbdrck/vx300s_mujoco_envs>`_), which implements
the ViperX-300 S **reach**, **push**, and **pick-and-place** tasks on
the MuJoCo backend.


1. Pick a starting point
------------------------

* **New robot, new task** — copy both layers from the MultiROS MuJoCo
  templates (``MyMujocoRobotEnv.py`` + ``MyMujocoTaskEnv.py``).
* **Existing robot, new task** — copy only the task layer and inherit
  from the existing robot env (this is how ``vx300s_mujoco_envs``'s
  push task extends the same robot env the reach task uses).
* **Reach-like task** — start from the ``vx300s_mujoco_envs`` reach
  task and adapt.

Goal-conditioned tasks (suitable for HER) use the ``...GoalEnv.py``
templates and the ``multiros.envs.MujocoGoalEnv.MujocoGoalEnv`` base
class.

The MuJoCo tooling mirrors the Gazebo tooling one-to-one
(``mujoco_core`` / ``mujoco_models`` / ``mujoco_physics`` /
``MujocoBaseEnv``), so if you have built a Gazebo env the structure
will be familiar. See :doc:`mujoco_backend` for the full mapping.


2. Build the MJCF scene
-----------------------

This step has no Gazebo equivalent. Gazebo spawns models into a
running world; MuJoCo loads a single MJCF/XML scene when the server
starts. You provide that scene as a package asset.

* Start from the robot's MJCF (e.g. the MuJoCo Menagerie model).
  **Remove the native** ``<actuator>`` **block** — joints are driven
  through ``mujoco_ros_control``, and leaving the MJCF position
  actuators in place would fight the controller.
* Compose scenes with ``<include>``. ``vx300s_mujoco_envs`` uses a
  layered set: ``vx300s.xml`` (arm only) → ``vx300s_table_scene.xml``
  (arm + table + floor) → ``vx300s_push_scene.xml`` (table scene + a
  cube). Reuse keeps the arm/table identical across tasks.
* Mount the arm and the work surface consistently. In the example the
  arm base is at the world origin and the table top is at ``z = 0``,
  so the arm's kinematics and the task goal sampling do not change
  when the table is added; the table slab extends downward and the
  ground plane is dropped to the foot of its legs.

Validate the scene compiles before wiring anything else:

.. code-block:: python

   import mujoco
   mujoco.MjModel.from_xml_path("assets/<robot>_mjcf/<scene>.xml")


3. Implement the robot env
--------------------------

The robot env extends ``multiros.envs.MujocoBaseEnv.MujocoBaseEnv``
(or its goal variant). The base class handles the lifecycle — bringing
up the robot description, the ``robot_state_publisher`` and the ROS
controllers, and pausing/unpausing (or deterministically stepping) the
simulation — so your job is to fill in robot-side helpers
(``get_ee_pose()``, ``move_arm_joints(...)``, forward kinematics, etc.)
and the robot-side reset.

Two MuJoCo-specific constructor arguments matter:

* ``controlled_joints`` — the joints your task drives. The backend
  keeps only these joints' ``<transmission>`` elements in
  ``robot_description`` and strips the rest. This is required because
  ``mujoco_ros_control`` aborts if the URDF declares a transmission
  for a joint that is not in the MJCF (manufacturer URDFs commonly
  include a gripper or mimic fingers the MJCF omits).
* ``sim_step_mode`` / ``num_mujoco_steps`` — select the stepping
  regime (see step 6).

A typical robot env constructor forwards these to the base class::

   class MyMujocoRobotEnv(MujocoBaseEnv):
       def __init__(self, **kwargs):
           super().__init__(
               spawn_robot=load_robot,
               urdf_pkg_name="my_robot_description",
               urdf_file_name="my_robot.urdf.xacro",
               controllers_file="my_robot_control.yaml",
               controllers_list=["joint_state_controller", "arm_controller"],
               controller_package_name="my_mujoco_envs",
               controlled_joints=["joint1", "joint2", "joint3", ...],
               **kwargs,
           )


4. Implement the task env
-------------------------

The task env extends your robot env and defines the gymnasium
contract. Required overrides mirror the Gazebo guide:

* ``_set_action(action)`` — apply the action to the robot.
* ``_get_observation()`` — return the observation array (or dict for
  goal envs).
* ``_get_reward()`` (or ``compute_reward(...)`` for goal envs).
* ``_compute_terminated()`` / ``_compute_truncated()``.
* ``_set_init_params()`` — task-side reset (randomise the target,
  reposition objects).

Declare ``observation_space`` and ``action_space`` in ``__init__``
with ``gymnasium.spaces.Box`` (pass ``seed=`` for reproducibility), or
``Dict`` for goal envs.

**Objects (push / pick-and-place).** Add the object to the MJCF scene
as a body with a ``<freejoint/>`` so it moves under contact, then in
the task env reposition it each episode and read its pose for the
observation. There is no per-episode spawn/delete; you move the
existing body via the ``set_body_state`` service:

.. code-block:: python

   from multiros.utils import mujoco_models

   # episode reset: place the cube in its spawn region
   mujoco_models.mujoco_set_body_state(
       body_name="cube",
       pos_x=x, pos_y=y, pos_z=z,
       set_pose=True, set_twist=True,      # set_twist zeroes its velocity
       server_name=self.server_name)

   # observation: read the cube pose back
   _, pose, _, ok = mujoco_models.mujoco_get_body_state(
       body_name="cube", server_name=self.server_name)

This is the MuJoCo analogue of Gazebo's ``set_model_state`` /
``get_model_state``. Keep the object's **observation** bounds wider
than its **spawn** region — a pushed object travels into the goal
region, and the observation must still contain it.


5. Register with gymnasium
--------------------------

Register the env when its module is imported (the example does this at
the top of each task module):

.. code-block:: python

   from gymnasium.envs.registration import register

   register(
       id="MyMujocoReachSim-v0",
       entry_point="my_mujoco_envs.task_envs.reach.my_mujoco_reach:MyMujocoReachEnv",
       max_episode_steps=100,
   )


6. Smoke test
-------------

The env can bring the whole stack up itself (``launch_mujoco=True``,
``new_roscore=True``, ``load_robot=True`` — all default True), so a
smoke test is a single process:

.. code-block:: python

   import uniros as gym
   import my_mujoco_envs                 # triggers gymnasium.register

   env = gym.make("MyMujocoReachSim-v0")  # self-launches roscore + server + controllers
   obs, info = env.reset(seed=0)
   for _ in range(100):
       obs, reward, term, trunc, info = env.step(env.action_space.sample())
       if term or trunc:
           obs, info = env.reset()
   env.close()

To attach to a stack you started separately (useful while debugging
the bring-up), launch the package's launch file first, then construct
the env with ``launch_mujoco=False, new_roscore=False,
load_robot=False``.

For manipulation tasks, random joint actions rarely bring the
end-effector to the object, so they do not exercise contact. Add a
short scripted "poke" (IK the end-effector through the object and
check it moves) to confirm contact and the free-joint dynamics
independently of the policy. Once the env runs cleanly, plug it into a
training script — see :doc:`training`.


7. Stepping regimes
-------------------

``MujocoBaseEnv`` supports three regimes, selected per task:

* **Real-time** (default) — the UniROS paper real-time loop; physics
  is never paused and a timer refreshes observations. Matches the real
  robot, so policies transfer.
* **Paused MDP** (``realtime_mode=False``) — physics runs only during
  the action window, then pauses; every sample is the post-action
  world state.
* **Deterministic fast-step** (``sim_step_mode=2``) — the simulation
  is advanced explicitly by ``num_mujoco_steps`` with no wall-clock
  sleep, so training runs faster than real time.


Configuration via YAML
----------------------

As with the Gazebo envs, keep task parameters (action limits, object
regions, reward coefficients, tolerances) in a YAML file under
``config/`` and load it at construction:

.. code-block:: python

   from multiros.utils.ros_common import ros_load_yaml
   ros_load_yaml(pkg_name="my_mujoco_envs",
                 file_name="my_task_config.yaml", ns="/")
   self.reach_tolerance = rospy.get_param("/my_robot/reach_tolerance")

Keep the env package self-contained: ship its own task and training
configs rather than importing them from another package, so it can be
used with just MultiROS + ``sb3_ros_support``.


Common pitfalls
---------------

* **Transmission mismatch**. If ``mujoco_ros_control`` logs *"Could
  not initialize robot simulation interface"*, the URDF declares a
  transmission for a joint absent from the MJCF. Pass
  ``controlled_joints`` (env) and use the launch helper
  ``$(find multiros)/scripts/mujoco_filtered_description.py`` (launch
  files) so only the driven joints' transmissions are kept.
* **use_sim_time and resets**. The MuJoCo server publishes ``/clock``;
  a reset rewinds it, so any ``rospy.sleep`` straddling a reset must
  tolerate ``ROSTimeMovedBackwardsException``. The backend already
  guards its own sleeps; do the same in task code that sleeps.
* **Degenerate observation bounds**. A ``Box`` dimension whose min
  equals max (e.g. an object's z fixed to the table height) trips the
  gymnasium checker. Give every dimension a real range.
* **Object obs vs spawn region**. Bound the object's observation to
  cover spawn + goal + overshoot, not just the spawn region, or a
  pushed object leaves the observation space.
* **Safety floor for table tasks**. The per-link floor check is shared
  with the Gazebo envs. Its defaults suit reach (which never
  approaches the surface); for push/pick-and-place tune ``table_z`` /
  ``safety_z_margin`` in the task config so the arm can get low enough
  to contact the object without the action being rejected.
* **Seed leakage**. Use ``self.np_random`` (populated by the base
  class via ``super().reset(seed=seed)``), not ``np.random``.
