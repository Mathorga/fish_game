import pyglet

from amonite.node import PositionNode
from amonite.sprite_node import SpriteNode
from amonite.animation import Animation
from amonite.settings import SETTINGS
from amonite.settings import Keys

class LegNode(PositionNode):
    __slots__ = (
        "__batch",
        "sprite"
    )

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        batch: pyglet.graphics.Batch | None = None
    ) -> None:
        super().__init__(
            x = x,
            y = y,
            z = z
        )

        self.__batch: pyglet.graphics.Batch | None = batch

        ################ Sprite ################
        self.sprite: SpriteNode = SpriteNode(
            resource = Animation(source = "sprites/leg/leg_idle.json").content,
            x = SETTINGS[Keys.VIEW_WIDTH] / 2,
            y = SETTINGS[Keys.VIEW_HEIGHT] / 2,
            batch = batch
        )

    def update(self, dt: float) -> None:
        super().update(dt = dt)

        # Update sprite position.
        self.sprite.set_position(self.get_position())

    def delete(self) -> None:
        self.sprite.delete()
        super().delete()