
# UniROS: ROS-Based Reinforcement Learning Across Simulated and Real-World Robotics

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/uniros/badge/?version=latest)](https://uniros.readthedocs.io/en/latest/?badge=latest)

📚 **Full documentation**: [uniros.readthedocs.io](https://uniros.readthedocs.io/)

A comprehensive framework for reinforcement learning in robotics,
which allows users to train their robots in both simulated and real-world environments concurrently.
It simplifies the process of creating reinforcement learning environments for robots
and provides a unified interface for training
and evaluating the robots in both simulated and real-world environments.

## Overview
This repository, UniROS, is designed to integrate two separate repositories, [MultiROS](https://github.com/ncbdrck/multiros) and [RealROS](https://github.com/ncbdrck/realros), giving users the flexibility to use them either as standalone modules or as integrated parts of UniROS.

## Easiest install: one-shot script

If you're starting fresh on Ubuntu 20.04, run the bootstrap installer.
It installs ROS Noetic, UniROS (with MultiROS + RealROS as
submodules), sb3_ros_support, rl_environments (with all 4 robots'
vendor packages + supporting description-extras + cube tracker), and
rl_training_validation. Interactive by default; pass `-y` for an
unattended install.

```bash
git clone -b gymnasium https://github.com/ncbdrck/UniROS.git /tmp/uniros_bootstrap
bash /tmp/uniros_bootstrap/install_uniros_stack.sh                # interactive
bash /tmp/uniros_bootstrap/install_uniros_stack.sh -y             # unattended
bash /tmp/uniros_bootstrap/install_uniros_stack.sh -p ~/my_ws -y  # custom path
```

The script asks once whether to install all components or pick per-
component (ROS / UniROS / sb3_ros_support / rl_environments /
rl_training_validation). It refuses to run on anything other than
Ubuntu 20.04 because ROS Noetic doesn't officially support other
distros.

The manual setup paths below still work if you'd rather install
piece-by-piece.

## Don't have Ubuntu 20.04? Use Docker

If your host is Ubuntu 22.04 / 24.04, has a GPU with no Ubuntu 20.04
driver (RTX 50-series, etc.), or is Windows with WSL2, the same
stack ships as a Docker image in two variants:

```bash
git clone -b gymnasium https://github.com/ncbdrck/UniROS.git
cd UniROS/docker

# Default (CUDA-runtime base, ~16 GB)
./build.sh
./run_gui.sh

# — or — slim (no CUDA in image, ~12 GB; matches the TIAGo pattern)
./build.sh --slim
./run_gui.sh -t uniros:noetic-slim
```

If you're **already running Ubuntu 20.04 natively**, skip Docker and
use the one-shot installer above on the host directly. Native install
is faster, smaller, and avoids GL-passthrough / nvidia-container-toolkit
compatibility quirks that have surfaced on 20.04 hosts with newer
NVIDIA driver branches.

See [`docker/README.md`](docker/README.md) and the
[install guide's Docker section](https://uniros.readthedocs.io/en/latest/guides/install.html#option-c-docker)
for variant comparison, hardware passthrough, GPU notes, and bind-mounting a host
workspace for active development.


## Manual Installation steps 

Follow these steps:

```bash
cd ~/catkin_ws/src
git clone --recurse-submodules -b gymnasium https://github.com/ncbdrck/uniros

# update the submodules to the latest version
cd uniros
git checkout gymnasium
git submodule update --remote --recursive

# Install pip if you haven't already by running this command
sudo apt-get install python3-pip

# install the required Python packages for UniROS by running
cd ~/catkin_ws/src/uniros/uniros/
pip3 install -r requirements.txt

# Set the branch of the submodules to gymnasium
cd ~/catkin_ws/src/uniros/multiros
git checkout gymnasium
git pull
cd ~/catkin_ws/src/uniros/realros
git checkout gymnasium
git pull

# Before building the workspace, install the dependencies for MultiROS and RealROS
# You can find the dependencies in the respective repositories
# Not installing the dependencies may cause build errors

# build the workspace
cd ~/catkin_ws
rosdep install --from-paths src --ignore-src -r -y
catkin build
source devel/setup.bash
```

**Note:** MultiROS and RealROS have their own dependencies. Please follow the instructions in their respective repositories to install the dependencies.

## Usage

- Once you have set up UniROS, which includes MultiROS and RealROS, you can use each package to create reinforcement learning environments for your robots. 
- You can follow the instructions in the respective repositories to create your own environments. Use the provided [examples](https://github.com/ncbdrck/uniros_support_materials) as a starting point.
- Then, register the created environment with Gymnasium.  

    ```python
    # gymnasium registration - example
    from gymnasium.envs.registration import register
    
    register(
         id='MyEnv-v0',
         entry_point='multiros.templates.task_envs.MyTaskEnv:MyEnv',
         max_episode_steps=1000,
    )
    ```
- Finally instead of using `import gymnasium as gym` and then `gym.make('MyEnv-v0')` use the following to create the environment. This will create **separate processes** for each environment, making it possible to run multiple environments in parallel.
    ```python
    # for both simulated and real environments
    import uniros as gym
    env = gym.make('MyEnv-v0')
    ```

## Documentation

The full ecosystem documentation — installation, ready-made
environments, environment creation (sim and real), training with
any gymnasium-compatible framework, joint sim+real training, and
the API reference — lives at
[uniros.readthedocs.io](https://uniros.readthedocs.io/).

(Contributors who want to build the docs locally: see
[docs/guides/contributing](https://uniros.readthedocs.io/en/latest/guides/contributing.html#development-setup).)

## Cite

If you use UniROS in your research or work and would like to cite it, please cite the journal paper:

```bibtex
@article{kapukotuwa_uniros_2025,
	title = {{UniROS}: {ROS}-{Based} {Reinforcement} {Learning} Across {Simulated} and {Real}-{World} {Robotics}},
	shorttitle = {{UniROS}},
	doi = {10.3390/s25185679},
	journal = {Sensors},
	author = {Kapukotuwa, Jayasekara and Lee, Brian and Devine, Declan and Qiao, Yuansong},
	volume = {25},
	number = {18},
	month = sep,
	year = {2025},
	pages = {5679},
	publisher = {{MDPI}},
	url = {https://www.mdpi.com/1424-8220/25/18/5679},
}
```
The earlier conference paper on the MultiROS sub-package:

```bibtex
@inproceedings{kapukotuwa_multiros_2022,
	title = {{MultiROS}: {ROS}-{Based} {Robot} {Simulation} {Environment} for {Concurrent} {Deep} {Reinforcement} {Learning}},
	shorttitle = {{MultiROS}},
	doi = {10.1109/CASE49997.2022.9926475},
	booktitle = {2022 {IEEE} 18th {International} {Conference} on {Automation} {Science} and {Engineering} ({CASE})},
	author = {Kapukotuwa, Jayasekara and Lee, Brian and Devine, Declan and Qiao, Yuansong},
	month = aug,
	year = {2022},
	note = {ISSN: 2161-8089},
	pages = {1098--1103},
}
```

Repository:

```bibtex
@misc{uniros,
  author = {Kapukotuwa, Jayasekara},
  booktitle = {GitHub repository},
  publisher = {GitHub},
  title = {UniROS: ROS-Based Reinforcement Learning Across Simulated and Real-world Robotics},
  url = {https://github.com/ncbdrck/uniros},
  year = {2023}
}
```

## Contact

For questions, suggestions, or collaborations, feel free to reach out to the project maintainer at [j.kapukotuwa@research.ait.ie](mailto:j.kapukotuwa@research.ait.ie).
