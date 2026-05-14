Installation
============

The ecosystem targets **ROS Noetic** on **Ubuntu 20.04** with
**Python 3.8**, **Gazebo Classic 11**, **Gymnasium 0.29.1**, and
**Stable Baselines 3 2.x**.

The fastest installation path is to use the bootstrap script
shipped with ``rl_environments`` — it installs ROS, the four
framework packages, and the robot drivers in one go. The manual
path below is for users who want to understand every step or
who already have parts of the stack installed.


Option A — bootstrap script (recommended)
-----------------------------------------

If you don't yet have a catkin workspace or want the everything-bundle:

.. code-block:: bash

   cd ~
   git clone https://github.com/ncbdrck/rl_environments.git
   cd rl_environments

   chmod +x install_ros_rl.sh
   ./install_ros_rl.sh            # interactive
   # or
   ./install_ros_rl.sh -n         # non-interactive

The script installs ROS Noetic (if missing), the four framework
packages on the ``gymnasium`` branch, and the RX200 / Ned2 / UR5
robot drivers. Skip to :doc:`quickstart` once it finishes.


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

   sudo apt install python3-rosdep python3-rosinstall \\
                    python3-rosinstall-generator python3-wstool \\
                    build-essential
   sudo rosdep init
   rosdep update


2. Catkin tools + workspace
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   sudo apt-get install python3-catkin-tools

   mkdir -p ~/catkin_ws/src
   cd ~/catkin_ws/
   catkin build
   echo "source ~/catkin_ws/devel/setup.bash" >> ~/.bashrc
   source ~/.bashrc


3. System dependencies
~~~~~~~~~~~~~~~~~~~~~~

The framework needs xterm (for log windows), MoveIt (motion
planning), and PyKDL / kdl_parser_py / trac_ik (kinematics):

.. code-block:: bash

   sudo apt install \\
       xterm \\
       ros-noetic-moveit \\
       python3-pykdl \\
       ros-noetic-kdl-parser-py \\
       ros-noetic-trac-ik \\
       ros-noetic-urdfdom-py

The ``Kinematics_pykdl`` helper relies on a Noetic-compatible fork
of ``pykdl_utils`` and ``hrl_geom``:

.. code-block:: bash

   cd ~/catkin_ws/src
   git clone https://github.com/ncbdrck/hrl-kdl.git

   cd ~/catkin_ws/src/hrl-kdl/pykdl_utils
   python3 setup.py build
   sudo python3 setup.py install

   cd ~/catkin_ws/src/hrl-kdl/hrl_geom
   python3 setup.py build
   sudo python3 setup.py install


4. Clone the framework
~~~~~~~~~~~~~~~~~~~~~~

UniROS bundles MultiROS and RealROS as **git submodules**, so one
recursive clone gives you all three packages:

.. code-block:: bash

   cd ~/catkin_ws/src
   git clone --recurse-submodules -b gymnasium https://github.com/ncbdrck/uniros

   # Make sure every submodule is on the gymnasium branch
   cd ~/catkin_ws/src/uniros
   git checkout gymnasium
   git submodule update --remote --recursive

   cd ~/catkin_ws/src/uniros/multiros
   git checkout gymnasium && git pull

   cd ~/catkin_ws/src/uniros/realros
   git checkout gymnasium && git pull

If you already have MultiROS or RealROS cloned standalone, skip
``--recurse-submodules`` and use the existing clones; just be sure
they're on the ``gymnasium`` branch.

Clone the SB3 support package (separate repo, not a submodule):

.. code-block:: bash

   cd ~/catkin_ws/src
   git clone -b gymnasium https://github.com/ncbdrck/sb3_ros_support.git


5. Python dependencies
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   sudo apt-get install python3-pip

   pip3 install -r ~/catkin_ws/src/uniros/uniros/requirements.txt
   pip3 install -r ~/catkin_ws/src/uniros/multiros/requirements.txt
   pip3 install -r ~/catkin_ws/src/uniros/realros/requirements.txt
   pip3 install -r ~/catkin_ws/src/sb3_ros_support/requirements.txt


6. Build the workspace
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd ~/catkin_ws
   rosdep install --from-paths src --ignore-src -r -y
   catkin build
   source devel/setup.bash


7. Verify
~~~~~~~~~

.. code-block:: bash

   python3 -c "import uniros, multiros, realros, sb3_ros_support; print('OK')"


Optional: ready-made envs + training scripts
--------------------------------------------

To get pre-built RX200 / Ned2 / UR5 envs and SB3 training scripts:

.. code-block:: bash

   cd ~/catkin_ws/src
   git clone https://github.com/ncbdrck/rl_environments.git
   git clone https://github.com/ncbdrck/rl_training_validation.git

   cd ~/catkin_ws
   rosdep install --from-paths src --ignore-src -r -y
   catkin build
   source devel/setup.bash

See :doc:`envs_ready_made` for what's currently working out of the
box, and :doc:`training` for how to train one.


Robot-specific extras
---------------------

The pre-built envs need the corresponding manufacturer's ROS
packages. Install the ones you'll use:

**Trossen ReactorX-200** (Interbotix arms)

.. code-block:: bash

   curl 'https://raw.githubusercontent.com/Interbotix/interbotix_ros_manipulators/main/interbotix_ros_xsarms/install/amd64/xsarm_amd64_install.sh' > xsarm_amd64_install.sh
   chmod +x xsarm_amd64_install.sh
   ./xsarm_amd64_install.sh -d noetic -p ~/catkin_ws

**Niryo Ned 2**

.. code-block:: bash

   cd ~/catkin_ws/src
   git clone https://github.com/NiryoRobotics/ned_ros.git
   cd ned_ros
   git submodule update --init ros-foxglove-bridge
   pip install -r requirements.txt
   sudo apt install sqlite3 ffmpeg build-essential -y

**Universal Robots UR5**

.. code-block:: bash

   sudo apt install ros-noetic-universal-robots
   # or build from source
   cd ~/catkin_ws/src
   git clone -b noetic-devel https://github.com/ros-industrial/universal_robot.git

Then rebuild the workspace and source it again.


Next step
---------

Continue with :doc:`quickstart` to launch your first env.
