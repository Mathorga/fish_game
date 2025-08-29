from amonite.scene_node import SceneNode
from amonite.node import PositionNode

from character_node import CharacterNode

# Global active scene accessor.
ACTIVE_SCENE_SRC: str | None = None
ACTIVE_SCENE: SceneNode | None = None

# Main charactes' global accessors.
FISH: CharacterNode | None = None
LEG: CharacterNode | None = None

# Characters' controller index.
FISH_CONTROLLER: int = 0
LEG_CONTROLLER: int = 1
