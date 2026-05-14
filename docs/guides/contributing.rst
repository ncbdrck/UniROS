Contributing
============

The framework is split across six repositories. Three are public
and accept contributions; one (this docs hub) is also public; two
host application code that lives alongside the framework.


Repositories
------------

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Repository
     - Role
   * - https://github.com/ncbdrck/UniROS
     - Canonical home for the gym-proxy class and shared ROS
       utilities. Bug fixes here flow to multiros and realros via
       re-exports. Also hosts this documentation site.
   * - https://github.com/ncbdrck/multiros
     - Gazebo simulation layer.
   * - https://github.com/ncbdrck/realros
     - Real-hardware layer.
   * - https://github.com/ncbdrck/sb3_ros_support
     - Stable Baselines 3 wrappers.
   * - https://github.com/ncbdrck/rl_environments
     - Ready-made gymnasium environments (RX200, NED2, ...).
   * - https://github.com/ncbdrck/rl_training_validation
     - Training scripts that exercise the rl_environments envs.


Development setup
-----------------

Set up a Noetic catkin workspace as in :doc:`install`, then check
out the development branches you want to work on. Active work
usually happens on a feature or integration branch before merging
to the repo's default branch (``gymnasium`` for the four framework
repos, ``main`` for the application repos).

Run the test suites before committing — see :doc:`testing`.

For docs work specifically:

.. code-block:: bash

   cd ~/catkin_ws/src/UniROS
   pip install -r docs/requirements.txt
   sphinx-build -b html docs docs/_build/html

Open ``docs/_build/html/index.html`` in a browser to preview.

Before pushing docs changes, run the Python-code-block
syntax check that CI runs:

.. code-block:: bash

   python scripts/check_python_code_blocks.py docs -v

It compiles every ``.. code-block:: python`` snippet under
``docs/``. ``SyntaxError`` here usually means a trailing ``...``
inside a function call, a missing closing bracket, or a
pseudo-code snippet that should have been tagged ``.. code-block::
text`` (or any non-``python`` lexer) rather than ``python``.


Commit conventions
------------------

* Use focused commits, one logical change each.
* Lead with an imperative summary line under 72 characters.
* Body should explain the *why*, not the *what* — the diff already
  shows the what.
* Reference the affected package in the summary when it isn't
  obvious from the file paths.


Pull requests
-------------

* Open against the relevant repo's default branch.
* Include a one-paragraph context block (what changed, why, how to
  verify) in the PR description.
* If you've added or changed a public API, update the matching
  page under ``docs/api/`` and confirm the local Sphinx build
  succeeds.
* CI is green is a prerequisite; the workflow takes ~30 seconds
  per Python version once the cache is warm.
