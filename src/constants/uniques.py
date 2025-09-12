from amonite.scene_node import SceneNode
from amonite.node import PositionNode

from character_node import CharacterNode

# Constants:

# Global active scene accessor.
ACTIVE_SCENE_SRC: str | None = None
ACTIVE_SCENE: SceneNode | None = None

# Main charactes' global accessors.
FISH: CharacterNode | None = None
LEG: CharacterNode | None = None

# Characters' controller index.
FISH_CONTROLLER: int = 0
LEG_CONTROLLER: int = 1

# States:

# Tells whether the characted activated the level door or not.
FISH_DOOR_TRIGGERED: bool = False
LEG_DOOR_TRIGGERED: bool = False