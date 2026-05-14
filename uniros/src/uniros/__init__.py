# Re-exports for the UniROS public API.
#
# Round 8 split the actual proxy implementation out into
# ``uniros._proxy.GymProxy``. The names below are preserved for
# backwards compatibility:
#
#   uniros.make           - drop-in for gym.make / gymnasium.make
#   uniros.uniros_gym     - the canonical proxy class (historical alias)
#   uniros.GymProxy       - same class, canonical name

from uniros._proxy import GymProxy
from uniros.core import uniros_gym

make = uniros_gym.make

__all__ = ["GymProxy", "uniros_gym", "make"]
