Docker
======

The UniROS stack targets **ROS Noetic on Ubuntu 20.04**. Many modern
hosts can't install Noetic natively — Ubuntu 22.04 / 24.04 OEM
laptops, machines whose GPUs need a newer-than-Noetic-supported
driver toolchain, Windows-with-WSL2 dev boxes. Docker is the
supported path for those users.

The image bakes the full installer output into an Ubuntu 20.04 +
ROS Noetic container: framework packages (UniROS, MultiROS, RealROS,
``sb3_ros_support``), application packages (``rl_environments``,
``rl_training_validation``), the four robots' description-extras
helpers, robot vendor packages (Interbotix RX200 + VX300S, Niryo
Ned2, UR5e + Robotiq), and ``rl_envs_cube_tracker``. Same install
logic as the bootstrap script — there's a single source of truth.


When to use Docker
------------------

* Your host runs Ubuntu 22.04 / 24.04 and you can't downgrade.
* Your GPU's driver stack doesn't have first-class Ubuntu 20.04
  support, or your modern PyTorch / CUDA combination needs a Python
  newer than the 3.8 that ships with Ubuntu 20.04 / Noetic.
* You're on Windows with WSL2.
* You want a reproducible, throw-away environment for CI or for
  reproducing the paper's results without committing your dev
  machine to Noetic.

A native Ubuntu 20.04 install (see :doc:`install` Option A or B) is
still the fastest path if your host already runs that distribution.


What works today
----------------

* **Image build** with the full UniROS stack baked in (single
  ``./build.sh``).
* **Headless run** — drops you into a bash shell with the
  workspace sourced. Suitable for training scripts, ``roscore``,
  ``rospy``, and headless Gazebo.
* **GUI run** — Gazebo and RViz windows render on the host
  display via `rocker <https://github.com/osrf/rocker>`_. Auto-detects
  NVIDIA for hardware-accelerated rendering; falls back to software.
* **Hardware passthrough** — USB-attached arms via ``--device``,
  network-attached arms via ``--network=host``.
* **Bind-mount a host workspace** for active development — edit
  source files in your IDE on the host, the container sees changes
  immediately.
* **Non-root user** matching your host UID/GID by default, so
  ``catkin build`` results in the container don't end up
  root-owned on the host.


Quick start
-----------

.. code-block:: bash

   git clone -b gymnasium https://github.com/ncbdrck/UniROS.git
   cd UniROS/docker
   ./build.sh         # 30–60 min first build; tags 'uniros:noetic'

   ./run.sh           # headless
   ./run_gui.sh       # GUI (Gazebo, RViz) via rocker

The same ``docker/`` tree (canonical in UniROS, byte-identical
copies in MultiROS, RealROS, ``sb3_ros_support``, ``rl_environments``,
``rl_training_validation``) ships in every ecosystem repo so you can
build the image from whichever repo you cloned first.


Hardware passthrough
--------------------

**Network-attached robots** (Niryo Ned2, UR5e) work out of the box.
``run.sh`` enables ``--network=host`` by default, so any
``ROS_MASTER_URI`` you set inside the container reaches the robot's
onboard rosmaster:

.. code-block:: bash

   ./run.sh
   # then inside the container:
   export ROS_MASTER_URI=http://ned2.local:11311
   rostopic list

**USB-attached arms** (Interbotix RX200 / VX300S over U2D2) need two
host-side steps:

1. Install the Interbotix udev rules on the **host**. The installer
   detects ``UNIROS_INSTALL_IN_DOCKER=1`` and skips udev inside the
   container (no udevd to talk to). From the host workspace:

   .. code-block:: bash

      sudo cp ~/uniros_ws/src/interbotix_ros_core/interbotix_ros_xseries/interbotix_xs_sdk/99-interbotix-udev.rules \
              /etc/udev/rules.d/
      sudo udevadm control --reload-rules && sudo udevadm trigger

2. Edit ``docker/run.sh`` (or ``run_gui.sh``) and uncomment the
   ``--device=/dev/ttyDXL:/dev/ttyDXL`` line.

**GPU access** for Gazebo hardware rendering or for in-container
ML uses NVIDIA's `Container Toolkit <https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html>`_.
Once installed, uncomment ``--gpus all`` in ``run.sh``, or
``run_gui.sh`` will detect and use NVIDIA automatically via rocker's
``--nvidia`` flag.


Active development
------------------

To edit source files on the host with your IDE while the container
runs builds and tests, bind-mount your host workspace at the
container's workspace path:

.. code-block:: bash

   ./run.sh -w ~/uniros_ws
   ./run_gui.sh -w ~/uniros_ws

The host workspace must be a fully bootstrapped catkin workspace —
either built by ``install_uniros_stack.sh`` on a native Ubuntu
20.04 host, or by a prior turn-key container build whose
``/home/uniros/uniros_ws`` was copied out. ``catkin build`` inside
the container writes ``build/`` and ``devel/`` to the host workspace
with your host UID, because ``build.sh`` matched UID/GID at image
build time.


Roadmap
-------

The image currently runs both the ROS env and the learning
algorithm inside the same container. That's fine for ``sb3_ros_support``
and for any algorithm that can tolerate Python 3.8 (the version
Noetic pins). It's the wrong shape if you want to run a modern
learning stack — for example, current PyTorch requires Python 3.9
or newer; the latest CUDA / Blackwell wheels are only published for
newer Python interpreters; many recent JAX / RL frameworks have
similar floors.

We're working on a **remote env mode** that splits the stack across
the container boundary:

* The container holds the ROS env (rospy, Gazebo, MoveIt, the four
  robots' drivers) on the pinned Python 3.8 / Noetic side.
* The host holds the learner (any Python version, any CUDA, any
  PyTorch / JAX / Tianshou / CleanRL / hand-written loop).
* They communicate over a TCP socket that speaks a small Gymnasium
  RPC: ``reset``, ``step``, ``close``, plus the observation and
  action space metadata.

From the algorithm's perspective it stays a Gymnasium env —
``uniros.make("RX200ReacherSim-v0", remote="localhost:5555")`` returns
something with ``.reset()`` and ``.step()`` that you can hand to any
training loop. From the env's perspective, ``uniros-env-server``
inside the container hosts the env class and serves the RPC.

The pieces this needs — a versioned wire protocol, a codec that
covers ``Box`` / ``Dict`` / ``Discrete`` spaces, vectorised-env
support for SB3, structured error envelopes, an in-container
process-lifecycle equivalent of the existing in-process
``GymProxy.close()`` — make it a small subsystem rather than a
single edit, so it will land in a future release rather than the
current one.

Until that lands, the supported pattern is to run the whole stack
inside the container (training and env both) using
``sb3_ros_support`` or any other Gymnasium-compatible framework
that runs on Python 3.8.


Troubleshooting
---------------

**X11 forwarding doesn't work and the GUI run script errors out.**
Make sure ``rocker`` is installed on the host
(``sudo apt install python3-rocker``), that your ``$DISPLAY`` is set,
and that ``xhost +local:`` (or a more restrictive equivalent) has
allowed the container's X11 connections. On Windows / WSL2,
make sure WSLg is enabled (Windows 11 has it built in; Windows 10
needs the WSLg preview).

**``rosrun`` can't find a node after sourcing inside the container.**
The container's entrypoint is bash with ``/home/uniros/uniros_ws/devel/setup.bash``
sourced via ``~/.bashrc``. If you bind-mounted a host workspace,
make sure ``catkin build`` has run inside that workspace at least
once, and re-source ``devel/setup.bash``.

**``catkin build`` outputs end up root-owned on the host.**
You probably built the image with a UID that doesn't match your
host UID. Rebuild with ``./build.sh -u $(id -u) -g $(id -g)``, or
run via ``./run_gui.sh`` which uses rocker's ``--user`` flag to
layer your host UID at runtime.

**Network-attached robot isn't reachable from inside the container.**
``run.sh`` uses ``--network=host`` so the container shares your host's
network stack. If you're on macOS / Windows where host-mode networking
isn't fully supported, you'll need to publish the right ports
(``-p`` flags) or run the rosmaster inside the container and have the
robot point to it.


See also
--------

* The repo-local quick reference: ``docker/README.md`` in any
  ecosystem repo.
* :doc:`install` Option C — the install-page summary of Docker.
* The bootstrap installer for native installs:
  :doc:`install` Option A.
