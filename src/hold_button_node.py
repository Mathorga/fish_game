from typing import Callable
import pyglet

import amonite.controllers as controllers
from amonite.node import PositionNode
from amonite.sprite_node import SpriteNode
from amonite.animation import Animation
from amonite.collision.collision_node import CollisionNode
from amonite.collision.collision_node import CollisionType
from amonite.collision.collision_shape import CollisionRect
from amonite.collision.collision_node import CollisionMethod

from constants import collision_tags

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

        self.__on_triggered_on: Callable | None = on_triggered_on
        self.__on_triggered_off: Callable | None = on_triggered_off
        self.__batch: pyglet.graphics.Batch | None = batch

        ################################
        # Sprite.
        ################################
        self.sprite: SpriteNode = SpriteNode(
            resource = Animation(source = "sprites/buttons/button_up.json").content,
            x = x,
            y = y,
            z = -100.0,
            y_sort = False,
            batch = batch
        )
        ################################
        ################################

        ################################
        # Colliders.
        ################################
        self.__collider: CollisionNode = CollisionNode(
            x = x,
            y = y,
            collision_type = CollisionType.STATIC,
            active_tags = [],
            passive_tags = [
                collision_tags.PLAYER_COLLISION
            ],
            shape = CollisionRect(
                x = x,
                y = y,
                anchor_x = 0,
                anchor_y = 0,
                width = 16,
                height = 6,
                batch = batch
            ),
            on_triggered = self.__on_collision
        )
        self.__sensor: CollisionNode = CollisionNode(
            x = x,
            y = y,
            collision_type = CollisionType.STATIC,
            collision_method = CollisionMethod.PASSIVE,
            sensor = True,
            active_tags = [],
            passive_tags = [
                collision_tags.PLAYER_COLLISION
            ],
            shape = CollisionRect(
                x = x,
                y = y,
                anchor_x = -5,
                anchor_y = -2,
                width = 6,
                height = 3,
                batch = batch
            ),
            on_triggered = self.__on_sense
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.__collider)
        controllers.COLLISION_CONTROLLER.add_collider(self.__sensor)
        ################################
        ################################

    def __on_collision(self, tags: list[str], collider: CollisionNode, entered: bool) -> None:
        pass

    def __on_sense(self, tags: list[str], collider: CollisionNode, entered: bool) -> None:
        if entered and self.__on_triggered_on is not None:
            self.__on_triggered_on()
            return

        if not entered and self.__on_triggered_off is not None:
            self.__on_triggered_off()
            return
