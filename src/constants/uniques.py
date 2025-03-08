from amonite.scene_node import SceneNode
from amonite.node import PositionNode

# Global active scene accessor.
ACTIVE_SCENE: SceneNode | None = None

# Main charactes' global accessors.
FISH: PositionNode | None = None
LEG: PositionNode | None = None