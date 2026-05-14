# Public API for the UniROS package.
#
#   uniros.make           - drop-in for gym.make / gymnasium.make
#   uniros.GymProxy       - the canonical multiprocessing gym proxy
#   uniros.uniros_gym     - snake_case alias for GymProxy (kept for
#                           backwards compatibility)

from uniros._proxy import GymProxy
from uniros.core import uniros_gym

make = uniros_gym.make

__all__ = ["GymProxy", "uniros_gym", "make"]
