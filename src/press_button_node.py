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
from interactable.interactable import Interactable

class PressButtonNode(PositionNode, Interactable):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        allow_turning_off: bool = True,
        on_triggered_on: Callable | None = None,
        on_triggered_off: Callable | None = None,
        batch: pyglet.graphics.Batch | None = None
    ) -> None:
        PositionNode.__init__(
            self,
            x = x,
            y = y,
            z = z
        )
        Interactable.__init__(
            self,
            one_shot = not allow_turning_off
        )

        self.__on_triggered_on: Callable | None = on_triggered_on
        self.__on_triggered_off: Callable | None = on_triggered_off

        ################################
        # Sprite.
        ################################
        self.sprite: SpriteNode = SpriteNode(
            resource = Animation(source = "sprites/buttons/button_up.json").content,
            y_sort = False,
            batch = batch
        )
        self.add_component(self.sprite)
        ################################
        ################################

        ################################
        # Colliders.
        ################################
        self.__interact_trigger: CollisionNode = CollisionNode(
            collision_type = CollisionType.STATIC,
            collision_method = CollisionMethod.PASSIVE,
            sensor = True,
            active_tags = [],
            passive_tags = [
                collision_tags.INTERACTABLE
            ],
            shape = CollisionRect(
                anchor_x = 15,
                anchor_y = 15,
                width = 30,
                height = 30,
                batch = batch
            ),
            owner = self
        )
        self.add_component(self.__interact_trigger)
        controllers.COLLISION_CONTROLLER.add_collider(self.__interact_trigger)
        ################################
        ################################

    def interact(
        self,
        tags: list[str]
    ):
        super().interact(tags = tags)

        if self.on:
            self.sprite.set_image(Animation(source = "sprites/buttons/button_down.json").content)

            if self.__on_triggered_on is not None:
                self.__on_triggered_on()
        else:
            self.sprite.set_image(Animation(source = "sprites/buttons/button_up.json").content)

            if self.__on_triggered_off is not None:
                self.__on_triggered_off()
            return