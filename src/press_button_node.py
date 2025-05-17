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
from interactable import Interactable

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
    ):
        PositionNode.__init__(self, x, y, z)
        Interactable.__init__(self)

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

        ################################
        # Colliders.
        ################################
        self.__grab_trigger: CollisionNode = CollisionNode(
            x = x,
            y = y,
            collision_type = CollisionType.STATIC,
            collision_method = CollisionMethod.PASSIVE,
            sensor = True,
            active_tags = [],
            passive_tags = [
                collision_tags.INTERACTABLE
            ],
            shape = CollisionRect(
                x = x,
                y = y,
                anchor_x = 20,
                anchor_y = 20,
                width = 40,
                height = 40,
                batch = batch
            ),
            owner = self
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.__grab_trigger)
        ################################
        ################################

    def interact(self):
        return super().interact()