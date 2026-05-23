Installation
============

The ecosystem targets **ROS Noetic** on **Ubuntu 20.04** with
**Python 3.8**, **Gazebo Classic 11**, **Gymnasium 0.29.1**, and
**Stable Baselines 3 2.x**.

.. note::

   **ROS Noetic and Gazebo Classic are end-of-life as of 2025.**
   This framework is a research artifact targeting that pinned
   environment for reproducibility with the
   `published paper <https://www.mdpi.com/1424-8220/25/18/5679>`_.
   New production work should consider a ROS 2 / modern Gazebo
   migration — that's out of scope for the current codebase but
   tracked as future work.

The fastest path is the bootstrap script ``install_uniros_stack.sh``,
which installs ROS Noetic, the framework, all six application repos,
and every supported robot's vendor packages in one go. The manual
path below is for users who want to step through each piece.


Option A — bootstrap script (recommended for a fresh machine)
-------------------------------------------------------------

Identical copies of the bootstrap script live in every ecosystem
repo (UniROS, MultiROS, RealROS, ``sb3_ros_support``,
``rl_environments``, ``rl_training_validation``); run it from
whichever repo you cloned first.

.. code-block:: bash

   # Grab the canonical copy without cloning the whole UniROS tree
   curl -fsSL https://raw.githubusercontent.com/ncbdrck/UniROS/gymnasium/install_uniros_stack.sh \
        -o /tmp/install_uniros_stack.sh
   chmod +x /tmp/install_uniros_stack.sh

   # Interactive: prompts before each component, default workspace ~/uniros_ws
   bash /tmp/install_uniros_stack.sh

   # Non-interactive: assume yes to every prompt
   bash /tmp/install_uniros_stack.sh -y

   # Custom workspace location (path must end in ``_ws/`` or already
   # contain a ``src/`` subfolder)
   bash /tmp/install_uniros_stack.sh -p ~/my_ws -y

What the script installs:

* ROS Noetic (``ros-noetic-desktop-full``) and dependencies
  (xterm, MoveIt, PyKDL, ``hrl-kdl`` for ``pykdl_utils`` /
  ``hrl_geom``, trac_ik, urdfdom-py).
* A catkin workspace (default ``~/uniros_ws``) and ``catkin_tools``.
* The four framework packages: ``UniROS`` (recursively, pulling
  ``multiros`` and ``realros`` as submodules) and ``sb3_ros_support``.
* The two application packages: ``rl_environments`` and
  ``rl_training_validation``.
* Per-robot description-extras helpers:
  ``reactorx200_description``, ``niryo_ned2_description_extras``,
  ``viperx300s_description``, ``ur5e_description_extras``,
  plus the shared ``common-sensors``.
* Robot vendor packages: Interbotix (RX200 + VX300S), Niryo Ned2
  (``ned_ros``), Universal Robots (``universal_robot`` +
  ``ur_robot_driver`` + ``ur_calibration``), and the
  ``filesmuggler/robotiq`` driver for the UR5e gripper.
* ``rl_envs_cube_tracker`` — the AprilTag-based ``/cube_pose``
  publisher used by real push and pick-and-place envs.
* RealSense D405 SDK (Kinect v2 and ZED 2 drivers stay user-provided
  because they need vendor SDKs).

The script is **idempotent**: existing ROS installs, existing repo
clones, and pip packages that are already up to date are skipped.

After the script finishes, it prints next-step commands (listing
envs, smoke-training the RX200 reacher). Jump to :doc:`quickstart`
for the same flow with extra explanation.


Option B — manual installation
------------------------------


1. ROS Noetic
~~~~~~~~~~~~~

.. code-block:: bash

   sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
   sudo apt install curl
   curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
   sudo apt update
   sudo apt install ros-noetic-desktop-full

   echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc
   source ~/.bashrc

   sudo apt install python3-rosdep python3-rosinstall \
                    python3-rosinstall-generator python3-wstool \
                    build-essential
   sudo rosdep init
   rosdep update


2. Catkin tools + workspace
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   sudo apt-get install python3-catkin-tools

   mkdir -p ~/uniros_ws/src
   cd ~/uniros_ws/
   catkin build
   echo "source ~/uniros_ws/devel/setup.bash" >> ~/.bashrc
   source ~/.bashrc


3. System dependencies
~~~~~~~~~~~~~~~~~~~~~~

The framework needs xterm (for log windows), MoveIt (motion
planning), and PyKDL / kdl_parser_py / trac_ik (kinematics):

.. code-block:: bash

   sudo apt install \
       xterm \
       ros-noetic-moveit \
       python3-pykdl \
       ros-noetic-kdl-parser-py \
       ros-noetic-trac-ik \
       ros-noetic-urdfdom-py

The ``Kinematics_pykdl`` helper relies on a Noetic-compatible fork
of ``pykdl_utils`` and ``hrl_geom``:

.. code-block:: bash

   cd ~/uniros_ws/src
   git clone https://github.com/ncbdrck/hrl-kdl.git

   cd ~/uniros_ws/src/hrl-kdl/pykdl_utils
   python3 setup.py build
   sudo python3 setup.py install

   cd ~/uniros_ws/src/hrl-kdl/hrl_geom
   python3 setup.py build
   sudo python3 setup.py install


4. Clone the framework
~~~~~~~~~~~~~~~~~~~~~~

UniROS bundles MultiROS and RealROS as **git submodules**, so one
recursive clone gives you all three packages:

.. code-block:: bash

   cd ~/uniros_ws/src
   git clone --recurse-submodules -b gymnasium https://github.com/ncbdrck/UniROS

   # Make sure every submodule is on the gymnasium branch
   cd ~/uniros_ws/src/UniROS
   git checkout gymnasium
   git submodule update --remote --recursive

If you already have MultiROS or RealROS cloned standalone, skip
``--recurse-submodules`` and use the existing clones; just be sure
they're on the ``gymnasium`` branch.

.. admonition:: Workspace layouts
   :class: note

   Two layouts are supported, both work:

   **A. Submodule layout (recommended for new users / RTD)** —
   one recursive clone of UniROS pulls MultiROS and RealROS in as
   submodules under ``UniROS/multiros/`` and ``UniROS/realros/``.

   **B. Sibling layout (common for active developers)** — clone
   MultiROS and RealROS as standalone packages alongside UniROS in
   the catkin ``src/`` directory. This is what an active developer
   often ends up with: catkin can't host two packages with the
   same ``<name>``, so once you start editing MultiROS or RealROS
   directly it's easier to have them as siblings of UniROS rather
   than as nested submodules.

   The framework and the docs work the same in both layouts.

Clone ``sb3_ros_support`` and the two application packages
(separate repos, not submodules):

.. code-block:: bash

   cd ~/uniros_ws/src
   git clone -b gymnasium https://github.com/ncbdrck/sb3_ros_support.git
   git clone https://github.com/ncbdrck/rl_environments.git
   git clone https://github.com/ncbdrck/rl_training_validation.git


5. Python dependencies
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   sudo apt-get install python3-pip

   pip3 install -r ~/uniros_ws/src/UniROS/uniros/requirements.txt
   pip3 install -r ~/uniros_ws/src/UniROS/multiros/requirements.txt
   pip3 install -r ~/uniros_ws/src/UniROS/realros/requirements.txt
   pip3 install -r ~/uniros_ws/src/sb3_ros_support/requirements.txt
   pip3 install -r ~/uniros_ws/src/rl_environments/requirements.txt


6. Build the workspace
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd ~/uniros_ws
   rosdep install --from-paths src --ignore-src -r -y
   catkin build
   source devel/setup.bash


7. Verify
~~~~~~~~~

.. code-block:: bash

   python3 -c "import uniros, multiros, realros, sb3_ros_support, rl_environments; print('OK')"


Robot-specific extras
---------------------

The pre-built envs need each robot's vendor ROS packages plus the
per-robot description-extras helper repo (table / cube / Kinect
wrap; ``install_uniros_stack.sh`` clones all of them in one pass).
Install the ones you'll use:

**Trossen ReactorX-200 + ViperX-300S** (Interbotix arms)

.. code-block:: bash

   cd ~/uniros_ws/src
   git clone -b noetic https://github.com/Interbotix/interbotix_ros_core.git
   git clone -b noetic https://github.com/Interbotix/interbotix_ros_manipulators.git
   git clone -b noetic https://github.com/Interbotix/interbotix_ros_toolboxes.git

   # Description-extras helpers (table / cube / Kinect wraps)
   git clone https://github.com/ncbdrck/reactorx200_description.git
   git clone https://github.com/ncbdrck/viperx300s_description.git
   git clone https://github.com/ncbdrck/common-sensors.git

The Interbotix repos ship CATKIN_IGNORE markers in some subfolders
the framework needs; ``install_uniros_stack.sh`` removes them
automatically. If you cloned manually, see the script's
``install_rl_environments`` step for the list of files to delete.

**Niryo Ned 2**

.. code-block:: bash

   cd ~/uniros_ws/src
   git clone https://github.com/NiryoRobotics/ned_ros.git
   cd ned_ros
   git submodule update --init ros-foxglove-bridge
   pip install -r requirements.txt
   sudo apt install sqlite3 ffmpeg build-essential -y

   cd ~/uniros_ws/src
   git clone https://github.com/ncbdrck/niryo_ned2_description_extras.git

**Universal Robots UR5e + Robotiq 2F-85**

.. code-block:: bash

   sudo apt install ros-noetic-ur-robot-driver ros-noetic-ur-calibration

   cd ~/uniros_ws/src
   git clone -b noetic-devel https://github.com/ros-industrial/universal_robot.git
   git clone https://github.com/filesmuggler/robotiq.git
   git clone https://github.com/ncbdrck/ur5e_description_extras.git

The UR5e real launch wrapper (``ur5e_real.launch``) is still pending
in ``ur5e_description_extras``; sim is fully supported.

**Real push / pick-and-place envs (any robot)**

Push and PnP real envs subscribe to ``/cube_pose`` for the cube's
pose. The publisher lives in a separate helper repo:

.. code-block:: bash

   cd ~/uniros_ws/src
   git clone https://github.com/ncbdrck/rl_envs_cube_tracker.git

See ``rl_envs_cube_tracker/README.md`` for camera-driver setup
(Kinect v2, ZED 2, and D405 are supported; D405 is the only one the
bootstrap script installs) and for per-camera-per-robot extrinsic
calibration instructions.

Then rebuild the workspace and source it again.


Next step
---------

Continue with :doc:`quickstart` to launch your first env.
