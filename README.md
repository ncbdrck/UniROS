
# UniRos Repository

## Overview
This repository, `uniros`, is designed to integrate two separate repositories, `multiros` and `realros`, giving users the flexibility to use them either as standalone modules or as integrated parts of `uniros`.

## Options for Setup
There are two ways to set up this repository:

1. **As an Integrated System (with Submodules):** Use this option if you do not have `multiros` and `realros` already set up. `uniros` will include both as submodules.

2. **Using Existing `multiros` and `realros`:** Choose this if you already have these repositories cloned and set up independently. 

## Pre-Setup: Check Existing Repositories
Before proceeding with the setup, determine if you already have `multiros` and `realros` on your system. Run the provided `check_repos.sh` script to automatically check for these repositories:

```bash
./check_repos.sh
```

If the script finds the repositories, follow the instructions for using existing repositories. If not, proceed with the integrated system setup.

## Setup as an Integrated System
If you do not have `multiros` and `realros`, or you wish to use them as submodules of `uniros`, follow these steps:

```bash
git clone --recurse-submodules https://github.com/ncbdrck/uniros
```

## Setup Using Existing `multiros` and `realros`
If you have existing clones of `multiros` and `realros`, follow these instructions:

```bash
git clone https://github.com/ncbdrck/uniros

```

## Script: `check_repos.sh`
Below is the `check_repos.sh` script. Save this in your `uniros` directory and run it to check if `multiros` and `realros` are already downloaded.

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
MULTIROS_DIR="path/to/multiros"
REALROS_DIR="path/to/realros"

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

