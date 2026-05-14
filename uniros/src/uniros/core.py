#!/bin/python3
"""
Re-export of the canonical gym proxy.

The actual implementation lives in ``uniros._proxy.GymProxy`` so
that multiros and realros can re-export the exact same class
without code duplication. The historical name ``uniros_gym``
(lowercase, snake_case) is preserved here as an alias.

Usage:
    from uniros.core import uniros_gym as gym
    env = gym.make("env_name", args)
    env.reset()
"""

from uniros._proxy import GymProxy

# Historical class name. Preserve the lowercase/snake_case spelling
# the public API used before Round 8.
uniros_gym = GymProxy

__all__ = ["GymProxy", "uniros_gym"]
