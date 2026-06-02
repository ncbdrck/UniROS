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
