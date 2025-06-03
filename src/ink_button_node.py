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

class Direction(str, Enum):
    UP = "up"
    DONW = "down"
    LEFT = "left"
    RIGHT = "right"

class InkButtonNode(PositionNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        button_anchor: Direction = Direction.LEFT,
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

        match button_anchor:
            case Direction.DONW:
                sprite_rotation = 0.0
                collider_width = 16
                collider_height = 6
                collider_anchor_y_offset = -5
            case Direction.UP:
                sprite_rotation = 180.0
                collider_width = 16
                collider_height = 6
                collider_anchor_y_offset = 5
            case Direction.LEFT:
                sprite_rotation = 90.0
                collider_width = 6
                collider_height = 16
                collider_anchor_x_offset = -5
            case Direction.RIGHT:
                sprite_rotation = 270.0
                collider_width = 6
                collider_height = 16
                collider_anchor_x_offset = 5

        ################################
        # Sprite.
        ################################
        self.sprite: SpriteNode = SpriteNode(
            resource = Animation(source = "sprites/buttons/button_up.json").content,
            y_sort = False,
            batch = batch
        )
        self.sprite.sprite.rotation = sprite_rotation
        self.add_component(self.sprite)
        ################################
        ################################

        ################################
        # Colliders.
        ################################
        self.__sensor: CollisionNode = CollisionNode(
            collision_type = CollisionType.STATIC,
            collision_method = CollisionMethod.PASSIVE,
            sensor = True,
            active_tags = [],
            passive_tags = [
                collision_tags.INK
            ],
            shape = CollisionRect(
                anchor_x = int((collider_width / 2) - collider_anchor_x_offset),
                anchor_y = int((collider_height / 2) - collider_anchor_y_offset),
                width = collider_width,
                height = collider_height,
                batch = batch
            ),
            on_triggered = self.__on_sense
        )
        self.add_component(self.__sensor)
        controllers.COLLISION_CONTROLLER.add_collider(self.__sensor)
        ################################
        ################################

    def __on_sense(self, tags: list[str], collider: CollisionNode, entered: bool) -> None:
        if entered:
            if not self.__on:
                self.__on = True
                self.sprite.set_image(Animation(source = "sprites/buttons/button_down.json").content)

                if self.__on_triggered_on is not None:
                    self.__on_triggered_on()
                return

            # Only trigger off if allowed.
            if self.__on and self.__allow_turning_off:
                self.__on = False
                self.sprite.set_image(Animation(source = "sprites/buttons/button_up.json").content)

                if self.__on_triggered_off is not None:
                    self.__on_triggered_off()
                return
