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

class RedPlatformNode(PositionNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        batch: pyglet.graphics.Batch | None = None
    ):
        super().__init__(
            x = x,
            y = y,
            z = z
        )

        self.__on: bool = False
        self.__switching: bool = False

        collider_width: int = 16
        collider_height: int = 16
        collider_anchor_x_offset: int = 0
        collider_anchor_y_offset: int = 0

        ################################
        # Sprite.
        ################################
        self.sprite: SpriteNode = SpriteNode(
            resource = Animation(source = "sprites/platforms/platform_inactive.json").content,
            x = x,
            y = y,
            z = -100.0,
            y_sort = False,
            on_animation_end = self.__on_sprite_animation_end,
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
            collision_method = CollisionMethod.PASSIVE,
            active_tags = [],
            passive_tags = [
                collision_tags.PLAYER_COLLISION
            ],
            shape = CollisionRect(
                x = x,
                y = y,
                anchor_x = (collider_width / 2) - collider_anchor_x_offset,
                anchor_y = (collider_height / 2) - collider_anchor_y_offset,
                width = collider_width,
                height = collider_height,
                batch = batch
            ),
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.__collider)
        ################################
        ################################

    def __on_sprite_animation_end(self) -> None:
        if not self.__switching:
            return

        self.sprite.set_image(Animation(source = "sprites/platforms/platform_inactive.json" if self.__on else "sprites/platforms/platform_active.json").content)

    def trigger_on(self) -> None:
        self.__switching = True
        self.sprite.set_image(Animation(source = "sprites/platforms/platform_activating.json").content)

    def trigger_off(self) -> None:
        self.__on = False
        self.sprite.set_image(Animation(source = "sprites/platforms/platform_inactive.json").content)
