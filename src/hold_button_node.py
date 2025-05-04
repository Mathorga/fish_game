from typing import Callable
import pyglet

from amonite.node import PositionNode
from amonite.sprite_node import SpriteNode
from amonite.animation import Animation
from amonite.settings import SETTINGS
from amonite.settings import Keys

class HoldButtonNode(PositionNode):
    def __init__(
        self,
        x = 0.0,
        y = 0.0,
        z = 0.0,
        on_triggered_on: Callable | None = None,
        on_triggered_off: Callable | None = None,
        batch: pyglet.graphics.Batch | None = None
    ):
        super().__init__(
            x = x,
            y = y,
            z = z
        )

        self.__on_triggered_on: Callable | None = on_triggered_on,
        self.__on_triggered_off: Callable | None = on_triggered_off,
        self.__batch: pyglet.graphics.Batch | None = batch

        ################################
        # Sprite.
        ################################
        self.sprite: SpriteNode = SpriteNode(
            resource = Animation(source = "sprites/buttons/button_up.json").content,
            x = x,
            y = x,
            y_sort = False,
            batch = batch
        )
        ################################
        ################################