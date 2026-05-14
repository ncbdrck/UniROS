from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

# fetch values from package.xml
setup_args = generate_distutils_setup(
    name="uniros",
    packages=['uniros'],
    package_dir={'': 'src'},

    description="ROS-Based Reinforcement Learning Across Simulated and Real-world Robotics",
    url="https://github.com/ncbdrck/uniros/",
    keywords=['ROS', 'reinforcement learning', 'machine-learning', 'gym', 'robotics', 'openai'],

    author='Jayasekara Kapukotuwa',
    author_email='j.kapukotuwa@research.ait.ie',

    license="MIT",
)

setup(**setup_args)
