
# UniROS: ROS-Based Reinforcement Learning Across Simulated and Real-world Robotics

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

## Options for Setup
There are two ways to set up this repository:

1. **As an Integrated System (with Submodules):** Use this option if you do not have [MultiROS](https://github.com/ncbdrck/multiros) and [RealROS](https://github.com/ncbdrck/realros) already set up. UniROS will include both as submodules.

2. **Using Existing MultiROS and RealROS:** Choose this if you already have these repositories cloned and set up independently. 

## Pre-Setup: Check Existing Repositories
Before proceeding with the setup, determine if you already have multiros and realros on your system. Run the provided `check_repos.sh` script to automatically check for these repositories:

```bash
./check_repos.sh
```

If the script finds the repositories, follow the instructions for using existing repositories. If not, proceed with the integrated system setup.

## 1. Setup as an Integrated System
If you do not have `MultiROS` and `RealROS`, or you wish to use them as submodules of `UniROS`, follow these steps:

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

# set the branch of the submodules to gymnasium
cd ~/catkin_ws/src/uniros/multiros
git checkout gymnasium
git pull
cd ~/catkin_ws/src/uniros/realros
git checkout gymnasium
git pull

# before building the workspace, install the dependencies for MultiROS and RealROS
# You can find the dependencies in the respective repositories
# Not installing the dependencies may cause build errors

# build the workspace
cd ~/catkin_ws
rosdep install --from-paths src --ignore-src -r -y
catkin build
source devel/setup.bash
```

**Note:** MultiROS and RealROS have their own dependencies. Please follow the instructions in their respective repositories to install the dependencies.

## 2. Setup Using Existing MultiROS and RealROS
If you have existing clones of `multiros` and `realros`, follow these instructions:

```bash
cd ~/catkin_ws/src
git clone -b gymnasium  https://github.com/ncbdrck/uniros

# continue with the installation as above
```
**Note:** Make sure that the branches of `multiros` and `realros` are set to `gymnasium`. If not, you can switch to the `gymnasium` branch by running the following commands:

```bash
cd ~/catkin_ws/src/multiros  # or the path to your multiros repository
git checkout gymnasium  # switch to the gymnasium branch
git pull  # to update the repository

cd ~/catkin_ws/src/realros  # or the path to your realros repository
git checkout gymnasium  # switch to the gymnasium branch
git pull  # to update the repository
```


## Usage

- Once you have set up UniROS, which includes MultiROS and RealROS, you can use each package to create reinforcement learning environments for your robots. 
- You can follow the instructions in the respective repositories to create your own environments. Use the provided [examples](https://github.com/ncbdrck/uniros_support_materials) as a starting point.
- Then, register the created environment with gymnasium.  

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

## Script: `check_repos.sh`
Below is the `check_repos.sh` script. Save it in your `home` directory and run it to check if `multiros` and `realros` are already downloaded.

```bash
#!/bin/bash

# Function to check if a directory is a Git repository
is_git_repo() {
    if git -C "$1" rev-parse 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Directories where multiros and realros might exist.
# Adjust these to match your workspace.
MULTIROS_DIR="$HOME/catkin_ws/src/multiros"
REALROS_DIR="$HOME/catkin_ws/src/realros"

# Check multiros
if [ -d "$MULTIROS_DIR" ] && is_git_repo "$MULTIROS_DIR"; then
    echo "multiros repository found at $MULTIROS_DIR"
else
    echo "multiros repository not found (looked in $MULTIROS_DIR)"
fi

# Check realros
if [ -d "$REALROS_DIR" ] && is_git_repo "$REALROS_DIR"; then
    echo "realros repository found at $REALROS_DIR"
else
    echo "realros repository not found (looked in $REALROS_DIR)"
fi
```

Update `MULTIROS_DIR` and `REALROS_DIR` to match where these repositories live in your workspace. The typical layout for a ROS catkin workspace is `~/<workspace_name>_ws/src/<repo_name>/`.

## Documentation

Full documentation for the ecosystem — installation, ready-made
environments, environment creation (sim and real), training with
any gymnasium-compatible framework, joint sim+real training, and
the API reference — lives in the [`docs/`](docs/) directory of
this repository and is built with Sphinx.

To preview locally:

```bash
cd ~/catkin_ws/src/UniROS
pip install -r docs/requirements.txt
sphinx-build -b html docs docs/_build/html
xdg-open docs/_build/html/index.html
```

## Cite

If you use UniROS in your research or work and would like to cite it, please cite the journal paper:

```bibtex
@Article{s25185679,
  AUTHOR  = {Kapukotuwa, Jayasekara and Lee, Brian and Devine, Declan and Qiao, Yuansong},
  TITLE   = {UniROS: ROS-Based Reinforcement Learning Across Simulated and Real-World Robotics},
  JOURNAL = {Sensors},
  VOLUME  = {25},
  YEAR    = {2025},
  NUMBER  = {18},
  PAGES   = {5679},
  URL     = {https://www.mdpi.com/1424-8220/25/18/5679},
  ISSN    = {1424-8220},
  DOI     = {10.3390/s25185679},
}
```

The earlier conference paper on the MultiROS sub-package:

```bibtex
@article{kapukotuwa_uniros_2025,
  title = {UniROS: A Unified Framework for ROS-Based Reinforcement Learning Across Simulated and Real-World Robotics},
  author = {Kapukotuwa, Jayasekara and Lee, Brian and Devine, Declan and Qiao, Yuansong},
  journal = {Sensors},
  volume = {25},
  number = {18},
  pages = {5679},
  year = {2025},
  publisher = {MDPI},
  doi = {10.3390/s25185679},
  url = {https://www.mdpi.com/1424-8220/25/18/5679}
}
```
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
