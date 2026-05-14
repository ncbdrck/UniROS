#!/bin/python3
"""
Re-export of the canonical gym proxy.

The implementation lives in :mod:`uniros._proxy` as
:class:`~uniros._proxy.GymProxy`. ``uniros_gym`` is a snake_case
alias kept for backwards compatibility — both names refer to the
same class object.

Usage::

    from uniros.core import uniros_gym as gym
    env = gym.make("env_name", args)
    env.reset()
"""

from uniros._proxy import GymProxy

# Snake_case alias kept for backwards compatibility with the older
# uniros public API.
uniros_gym = GymProxy

__all__ = ["GymProxy", "uniros_gym"]
