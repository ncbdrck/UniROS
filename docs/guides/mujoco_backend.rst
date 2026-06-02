MuJoCo backend (experimental)
=============================

.. admonition:: Available (experimental)
   :class: warning

   The MuJoCo simulation backend is **available but experimental**.
   It is usable today (reach, push, and pick-and-place envs run on
   it), but it is not yet in a stable release, and its APIs, defaults,
   and structure may still change. The default, supported backend
   remains **Gazebo** (see :doc:`env_creation_sim`). For install
   steps, see :ref:`mujoco-install-steps` below.

MultiROS is gaining a `MuJoCo <https://mujoco.org/>`_ simulation
backend (via `mujoco_ros_pkgs
<https://github.com/ubi-agni/mujoco_ros_pkgs>`_) as a drop-in
alternative to Gazebo. The goal is **architectural parity**: the
MuJoCo tooling mirrors the Gazebo tooling so that a robot/task
environment is built the same way regardless of which simulator runs
underneath. If you know how to build a Gazebo env
(:doc:`env_creation_sim`), the MuJoCo workflow should feel familiar —
only the simulator-specific pieces differ.


How it maps onto the Gazebo design
----------------------------------

Each Gazebo utility/base class has a MuJoCo sibling with the same role:

.. list-table::
   :widths: 40 40 20
   :header-rows: 1

   * - Gazebo
     - MuJoCo
     - Role
   * - ``multiros.utils.gazebo_core``
     - ``multiros.utils.mujoco_core``
     - Launch the server, pause/unpause, reset, step.
   * - ``multiros.utils.gazebo_models``
     - ``multiros.utils.mujoco_models``
     - Robot bring-up, scene management.
   * - ``multiros.utils.gazebo_physics``
     - ``multiros.utils.mujoco_physics``
     - Real-time factor, gravity, timestep.
   * - :class:`multiros.envs.GazeboBaseEnv.GazeboBaseEnv`
     - ``multiros.envs.MujocoBaseEnv.MujocoBaseEnv``
     - Standard env base class.
   * - :class:`multiros.envs.GazeboGoalEnv.GazeboGoalEnv`
     - ``multiros.envs.MujocoGoalEnv.MujocoGoalEnv``
     - Goal-conditioned (HER) base class.

The shared, simulator-agnostic utilities (``ros_common``,
``ros_controllers``, ``ros_kinematics``, ``ros_markers``, the
gym-proxy and the SB3 wrappers) are used unchanged. As with Gazebo,
a robot/task package only carries what is genuinely robot- or
task-specific: the URDF, the MJCF scene, controller/plugin configs,
and the action/observation/reward logic.


What differs from Gazebo
------------------------

MuJoCo is not Gazebo, so a few backend-specific points are worth
knowing when porting an env:

* **Scene model.** Gazebo spawns models into a running world; MuJoCo
  loads a single MJCF scene at server start. The robot geometry comes
  from that MJCF; ``mujoco_models`` brings up the ROS interfaces
  (robot description, ``robot_state_publisher``, controllers) on top.
* **Control via** ``mujoco_ros_control``. Joints are driven through the
  usual ``ros_control`` interfaces, so the trajectory-controller API
  (``/<ns>/arm_controller/command``) matches the Gazebo setup.
* **Transmission filtering.** ``mujoco_ros_control`` aborts if the URDF
  declares a ``<transmission>`` for a joint that is not in the MJCF
  (e.g. a gripper or mimic fingers absent from the model). The backend
  strips those automatically — a robot env passes ``controlled_joints``
  to the base class, and the launch helper
  ``scripts/mujoco_filtered_description.py`` does the same for launch
  files. The manufacturer URDF is reused unmodified.
* **Stepping regimes.** ``MujocoBaseEnv`` supports the same real-time
  loop as Gazebo (physics never pauses, a timer
  refreshes observations) and a paused-MDP loop, plus a deterministic
  fast-step mode (``sim_step_mode=2``) that advances the simulation
  explicitly with no wall-clock sleep, for training faster than
  real time.


.. _mujoco-install-steps:

Trying it
---------

Install the backend with the MultiROS installer's opt-in flag (it
fetches a prebuilt MuJoCo and clones ``mujoco_ros_pkgs`` plus the
example ``vx300s_mujoco_envs``)::

   ./install_uniros_stack.sh -m

Or, for the Docker image, bake the backend in at build time::

   cd UniROS/docker && ./build.sh --mujoco

A worked example lives in the standalone package
`vx300s_mujoco_envs <https://github.com/ncbdrck/vx300s_mujoco_envs>`_,
which validates the backend on the Trossen VX300S reach, push, and
pick-and-place tasks. It
mirrors the Gazebo VX300S envs but is built entirely from the MuJoCo
tooling. The one-command workflow matches the Gazebo envs::

   # self-launches roscore + the MuJoCo server + controllers
   rosrun vx300s_mujoco_envs vx300s_mujoco_reach_test.py

or in Python::

   import uniros as gym
   # Importing the task module registers its env id with gymnasium.
   from vx300s_mujoco_envs.task_envs.reach import vx300s_mujoco_reach  # noqa: F401
   env = gym.make("VX300SMujocoReacherSim-v0")
   obs, info = env.reset(seed=0)
   for _ in range(50):
       obs, reward, terminated, truncated, info = env.step(env.action_space.sample())
       if terminated or truncated:
           obs, info = env.reset()
   env.close()

Training reuses the same ``sb3_ros_support`` wrappers as the Gazebo
envs (SAC, TD3, …), with optional TensorBoard and Weights & Biases
monitoring.


Status and limitations
----------------------

* Not yet in a stable release; available on an experimental MultiROS
  branch (see install steps above).
* Implemented: VX300S reach, push, and pick-and-place, each with a
  goal-conditioned (HER) variant.
* Additional robots/tasks may follow.
* APIs may change before this lands in a release.


Differences from the Gazebo backend
-----------------------------------

The MuJoCo and Gazebo backends are deliberately implemented as
sibling sub-systems (mirroring the way RealROS sits next to
MultiROS). They share the public Task/Robot env hooks
(``_set_action``, ``_get_observation``, ``compute_reward``,
``_compute_terminated``, ``_compute_truncated``,
``_set_init_params``, ``_check_connection_and_readiness``), so a
Task env that only overrides those ports unchanged between
backends. The differences below are at the **utility layer**
underneath, where each backend talks to its own simulator. They
mirror real differences in what each simulator offers, not parity
gaps to be papered over.

**Object spawn / remove.**
Gazebo exposes module-level free functions
(``gazebo_models.spawn_sdf_model_gazebo``,
``gazebo_models.remove_model_gazebo``) backed by stateless service
calls. MuJoCo has no runtime spawn / delete service; the only way to
change scene topology is to regenerate the MJCF and call
``~reload``. The framework wraps this in a stateful
``MujocoSceneManager`` class
(``multiros.utils.mujoco_models.MujocoSceneManager``): construct it
with your base MJCF scene and call ``spawn_primitive``,
``spawn_model``, and ``remove_model`` on the instance. Each call
re-initialises the whole simulation, so it is suited to per-episode
scene changes rather than per-step updates. To reposition an object
that is already in the scene (declared with a free joint), use
``mujoco_set_body_state`` — much cheaper than a reload.

**Model state vs body state.**
Gazebo's accessors are named ``gazebo_get_model_state`` /
``gazebo_set_model_state`` because the Gazebo service operates on
named models with a configurable reference frame. MuJoCo's
underlying service operates on bodies (with the constraint that
``set_pose`` only applies to bodies whose parent joint is a free
joint), so the framework's accessors are
``mujoco_get_body_state`` / ``mujoco_set_body_state``. The names
match the simulator vocabulary; do not assume one maps to the
other transparently.

**Concurrency / per-instance isolation.**
Gazebo's parallelism uses distinct ``ROS_MASTER_URI`` *and*
``GAZEBO_MASTER_URI`` ports per instance. MuJoCo's parallelism
uses a single ``ROS_MASTER_URI`` per instance plus a ``server_name``
graph identifier (``mujoco_server`` by default) — the MuJoCo server
has no master-URI concept. Code that threads ``gazebo_port`` to
identify a Gazebo instance has to thread ``server_name`` for
MuJoCo.

**No model enumeration service.**
Gazebo's ``/gazebo/get_world_properties`` returns the list of model
names in the world; the framework uses this for spawn / remove
verify loops. ``mujoco_ros_pkgs`` exposes no equivalent service —
the scene topology is fixed in the MJCF and known to the env code.
Query a body's state by name with ``mujoco_get_body_state``; do not
attempt to enumerate the scene.

**Robot placement.**
Gazebo's ``spawn_robot_in_gazebo`` accepts the robot's spawn pose
as ``pos_x/y/z`` + ``ori_w/x/y/z`` kwargs because the robot is
spawned at runtime. MuJoCo loads the robot from the MJCF, so the
robot's pose lives in the MJCF ``<worldbody>``. The
``spawn_robot_in_mujoco`` signature does not take placement kwargs;
edit the MJCF to change the pose.

**Reset semantics.**
Gazebo distinguishes ``reset_world`` (data only, time preserved)
and ``reset_simulation`` (data + time) via the ``reset_mode``
kwarg. MuJoCo has a single ``~reset`` that calls ``mj_resetData``
and re-applies the configured initial joint states — there is no
world / simulation distinction. The MuJoCo backend therefore has no
``reset_mode`` kwarg; pass nothing.
