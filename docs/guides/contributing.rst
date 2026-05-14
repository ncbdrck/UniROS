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
       re-exports.
   * - https://github.com/ncbdrck/multiros
     - Gazebo simulation layer.
   * - https://github.com/ncbdrck/realros
     - Real-hardware layer.
   * - https://github.com/ncbdrck/sb3_ros_support
     - Stable Baselines 3 wrappers.
   * - https://github.com/ncbdrck/MultiROS_Real
     - This documentation site, plus internal review notes.


Development setup
-----------------

Set up a Noetic catkin workspace as in :doc:`install`, then check
out the development branches you want to work on. Most active work
happens on a ``cleanup-2026`` (or successor) branch before merging
to the public default.

Run the test suites before committing — see :doc:`testing`.

For docs work specifically:

.. code-block:: bash

   cd ~/catkin_ws/src/MultiROS_Real
   pip install -r docs/requirements.txt
   sphinx-build -b html docs docs/_build/html

Open ``docs/_build/html/index.html`` in a browser to preview.


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
