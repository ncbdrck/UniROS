UniROS / MultiROS / RealROS ecosystem
======================================

A ROS-based reinforcement-learning framework for robots, spanning
Gazebo simulation and real-world hardware. Built on Gymnasium and
Stable Baselines 3.

The ecosystem is split into four **core framework** packages plus
two **application** packages that ship pre-built environments and
training scripts. You can use the framework on its own or pull in
the applications as ready-made examples.

**Core framework**: UniROS, MultiROS, RealROS, ``sb3_ros_support``.

**Applications**: ``rl_environments``, ``rl_training_validation``.

.. list-table::
   :widths: 28 72
   :header-rows: 1

   * - Package
     - What it provides
   * - :doc:`api/uniros`
     - The unified abstraction layer. Hosts the canonical
       multiprocessing gym-env proxy class
       (:class:`uniros._proxy.GymProxy`) and the shared ROS utility
       modules used by every package below. Bundles MultiROS and
       RealROS as git submodules.
   * - :doc:`api/multiros`
     - Gazebo-based simulation environments. Spawn multiple gym
       envs in parallel against a single rosmaster, run roscores
       on arbitrary ports, manage Gazebo physics.
   * - :doc:`api/realros`
     - The real-hardware counterpart to MultiROS. Same gym API,
       talks to physical robots instead of Gazebo.
   * - :doc:`api/sb3_ros_support`
     - Stable Baselines 3 algorithm wrappers (PPO, A2C, DDPG, TD3,
       SAC, DQN, plus goal-conditioned variants) configured for
       ROS-based training scripts.
   * - :doc:`api/rl_environments`
     - Pre-built gym environments for the supported robots and tasks.
   * - :doc:`api/rl_training_validation`
     - Working training and validation scripts for the pre-built envs.

.. toctree::
   :maxdepth: 2
   :caption: Get started

   guides/install
   guides/quickstart
   guides/overview

.. toctree::
   :maxdepth: 2
   :caption: Environments

   envs/index
   guides/env_templates
   guides/env_creation_sim
   guides/env_creation_real

.. toctree::
   :maxdepth: 2
   :caption: Training

   guides/training
   guides/joint_sim_real_training
   guides/using_trained_models

.. toctree::
   :maxdepth: 2
   :caption: API reference

   api/uniros
   api/multiros
   api/realros
   api/sb3_ros_support
   api/rl_environments
   api/rl_training_validation

.. toctree::
   :maxdepth: 1
   :caption: Development

   guides/testing
   guides/contributing
   guides/limitations


About these docs
----------------

This documentation was drafted in collaboration with two AI
assistants — Anthropic's Claude (for writing and structure) and
OpenAI's Codex CLI (for review passes) — working from the UniROS
codebase, the *Sensors* paper, and design decisions made by the
author. Each change was reviewed before being committed.

That said, AI-assisted docs can still contain hallucinated APIs,
stale examples, or subtle factual errors. **If you find an
inaccuracy, please open an issue at**
`github.com/ncbdrck/UniROS/issues <https://github.com/ncbdrck/UniROS/issues>`_.


Citation
--------

If this ecosystem is useful in your work, please cite the paper:

.. code-block:: bibtex

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


Indices
-------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
