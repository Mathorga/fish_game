from enum import Enum
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

class InkButtonNode(PositionNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        allow_turning_off: bool = True,
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
        self.__allow_turning_off: bool = allow_turning_off
        self.__on: bool = False

        sprite_rotation: float = 0.0
        collider_width: int = 0
        collider_height: int = 0
        collider_anchor_x_offset: int = 0
        collider_anchor_y_offset: int = 0

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
        self.sprite.sprite.rotation = sprite_rotation
        ################################
        ################################

        # TODO Remove.
        ################################
        # Colliders.
        ################################
        self.__sensor: CollisionNode = CollisionNode(
            x = x,
            y = y,
            collision_type = CollisionType.STATIC,
            collision_method = CollisionMethod.PASSIVE,
            sensor = True,
            active_tags = [],
            passive_tags = [
                collision_tags.INK
            ],
            shape = CollisionRect(
                x = x,
                y = y,
                anchor_x = (collider_width / 2) - collider_anchor_x_offset,
                anchor_y = (collider_height / 2) - collider_anchor_y_offset,
                width = collider_width,
                height = collider_height,
                batch = batch
            )
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.__sensor)
        ################################
        ################################