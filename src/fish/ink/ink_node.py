import pyglet

from amonite.node import PositionNode
from amonite.sprite_node import SpriteNode
from amonite.animation import Animation

class InkNode(PositionNode):
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

        self.sprite: SpriteNode = SpriteNode(
            resource = Animation(source = "sprites/fish/ink_fly.json").content,
            x = self.x,
            y = self.y,
            z = self.z - 100,
            y_sort = False,
            batch = batch
        )

    def delete(self) -> None:
        self.sprite.delete()