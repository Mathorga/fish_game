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

sprite_on_file: str = "sprites/platforms/platform_active.json"
sprite_off_file: str = "sprites/platforms/platform_inactive.json"
sprite_on_to_off_file: str = "sprites/platforms/platform_activating.json"
sprite_off_to_on_file: str = "sprites/platforms/platform_inactive.json"

class RedPlatformNode(PositionNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        starts_on: bool = False,
        batch: pyglet.graphics.Batch | None = None
    ):
        super().__init__(
            x = x,
            y = y,
            z = z
        )

        self.__on: bool = starts_on
        self.__switching: bool = False

        collider_width: int = 16
        collider_height: int = 16
        collider_anchor_x_offset: int = 0
        collider_anchor_y_offset: int = 0

        ################################
        # Sprite.
        ################################
        self.sprite: SpriteNode = SpriteNode(
            resource = Animation(source = sprite_on_file if starts_on else sprite_off_file).content,
            y_sort = False,
            on_animation_end = self.__on_sprite_animation_end,
            batch = batch
        )
        self.add_component(self.sprite)
        ################################
        ################################

        ################################
        # Colliders.
        ################################
        self.__collider: CollisionNode = CollisionNode(
            collision_type = CollisionType.STATIC,
            collision_method = CollisionMethod.PASSIVE,
            active_tags = [],
            passive_tags = [
                collision_tags.PLAYER_COLLISION
            ],
            shape = CollisionRect(
                anchor_x = int((collider_width / 2) - collider_anchor_x_offset),
                anchor_y = int((collider_height / 2) - collider_anchor_y_offset),
                width = collider_width,
                height = collider_height,
                batch = batch
            ),
        )
        self.add_component(self.__collider)

        # Only activate the collider if starting on.
        if starts_on:
            controllers.COLLISION_CONTROLLER.add_collider(self.__collider)
        ################################
        ################################

    def update(self, dt: float) -> None:
        return super().update(dt)

    def __on_sprite_animation_end(self) -> None:
        if not self.__switching:
            return

        self.__switching = False

        if self.__on:
            self.sprite.set_image(Animation(source = sprite_on_file).content)
            controllers.COLLISION_CONTROLLER.add_collider(self.__collider)
        else:
            self.sprite.set_image(Animation(source = sprite_off_file).content)
            controllers.COLLISION_CONTROLLER.remove_collider(self.__collider)

    def trigger_on(self) -> None:
        if self.__on:
            return

        self.__switching = True
        self.__on = True
        self.sprite.set_image(Animation(source = sprite_on_to_off_file).content)

    def trigger_off(self) -> None:
        if not self.__on:
            return

        self.__switching = True
        self.__on = False
        self.sprite.set_image(Animation(source = sprite_off_to_on_file).content)
