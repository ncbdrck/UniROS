
# UniROS Repository

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
If you do not have MultiROS and RealROS, or you wish to use them as submodules of `UniROS`, follow these steps:

```bash
git clone --recurse-submodules https://github.com/ncbdrck/uniros
```

**Note:** MultiROS and RealROS have their own dependencies. Please follow the instructions in their respective repositories to install the dependencies.

## 2. Setup Using Existing MultiROS and RealROS
If you have existing clones of `multiros` and `realros`, follow these instructions:

```bash
git clone https://github.com/ncbdrck/uniros

```

## Script: `check_repos.sh`
Below is the `check_repos.sh` script. Save this in your `home` directory and run it to check if `multiros` and `realros` are already downloaded.

```bash
#!/bin/bash

# Function to check if a directory is a Git repository
is_git_repo() {
    if git -C $1 rev-parse 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Directories where multiros and realros might exist
MULTIROS_DIR="path/to/multiros"  # ~/catkin_ws/src/multiros
REALROS_DIR="path/to/realros"  # ~/catkin_ws/src/multiros

# Check multiros
if [ -d "$MULTIROS_DIR" ] && is_git_repo $MULTIROS_DIR; then
    echo "multiros repository found."
else
    echo "multiros repository not found."
fi

# Check realros
if [ -d "$rREALROS_DIR" ] && is_git_repo $REALROS_DIR; then
    echo "realros repository found."
else
    echo "realros repository not found."
fi
```

Replace `path/to/multiros` and `path/to/realros` with the actual paths where you expect these repositories to be.
Since we are working with ROS, the path typically should be in the format of `~/ros_workspace_ws/src/`.

## Cite

If you use UniROS in your research or work and would like to cite it, you can use the following citation:

Article:
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

Repositories:

```bibtex
@misc{realros,
  author = {Kapukotuwa, Jayasekara},
  booktitle = {GitHub repository},
  publisher = {GitHub},
  title = {RealROS: A Comprehensive Framework for Real-World Robotic Reinforcement Learning},
  url = {https://github.com/ncbdrck/realros},
  year = {2023}
}
```

```bibtex
@misc{multiros,
  author = {Kapukotuwa, Jayasekara},
  booktitle = {GitHub repository},
  publisher = {GitHub},
  title = {MultiROS: ROS-Based Robot Simulation Environment for Concurrent Deep Reinforcement Learning},
  url = {https://github.com/ncbdrck/multiros},
  year = {2022}
}
```

## Contact

For questions, suggestions, or collaborations, feel free to reach out to the project maintainer at [j.kapukotuwa@research.ait.ie](mailto:j.kapukotuwa@research.ait.ie).
