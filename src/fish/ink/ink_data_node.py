import math
from typing import Callable
import pyglet
import pyglet.math as pm

import amonite.controllers as controllers
from amonite.node import PositionNode
from amonite.sprite_node import SpriteNode
from amonite.animation import Animation
from amonite.collision.collision_node import CollisionNode
from amonite.collision.collision_node import CollisionType
from amonite.collision.collision_shape import CollisionRect
from amonite.settings import SETTINGS
from amonite.settings import GLOBALS
from amonite.settings import Keys

from constants import collision_tags


class InkDataNode(PositionNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        on_sprite_animation_end: Callable | None = None,
        on_collision: Callable | None = None,
        on_deletion: Callable | None = None,
        batch: pyglet.graphics.Batch | None = None
    ) -> None:
        PositionNode.__init__(self, x, y, z)

        self.__on_collision: Callable | None = on_collision
        self.__on_deletion: Callable | None = on_deletion
        self.__batch: pyglet.graphics.Batch | None = batch
        self.heading: float = 0.0


        ################################
        # Input movement.
        ################################
        self.move_vec: pm.Vec2 = pm.Vec2(0.0, 0.0)
        self.max_move_speed: float = 80.0
        self.move_accel: float = 20.0
        ################################
        ################################


        ################################
        # Gravity movement.
        ################################
        self.gravity_vec: pm.Vec2 = pm.Vec2(0.0, 0.0)
        self.target_gravity_speed: float = math.inf
        self.gravity_accel: pm.Vec2 = pm.Vec2(0.0, -300.0)
        ################################
        ################################


        ################################
        # Collision flags.
        ################################
        self.__ground_collision_ids: set[int] = set()
        self.grounded: bool = False
        self.in_water: bool = False
        ################################
        ################################

        self.shoot_vec: pm.Vec2 = pm.Vec2(0.0, 0.0)

        ################################
        # Sprite
        ################################
        self.__sprite: SpriteNode = SpriteNode(
            resource = Animation(source = "sprites/fish/ink_fly.json").content,
            x = 0.0,
            y = 0.0,
            z = 0.0,
            y_sort = False,
            on_animation_end = on_sprite_animation_end,
            batch = batch
        )
        self.add_component(self.__sprite)
        ################################
        ################################


        ################################
        # Colliders
        ################################
        self.__collider: CollisionNode = CollisionNode(
            x = 0.0,
            y = 0.0,
            collision_type = CollisionType.DYNAMIC,
            active_tags = [
                collision_tags.PLAYER_COLLISION,
                collision_tags.INK
            ],
            passive_tags = [],
            shape = CollisionRect(
                x = 0.0,
                y = 0.0,
                anchor_x = 3,
                anchor_y = 3,
                width = 6,
                height = 6,
                batch = batch
            ),
            on_triggered = self.on_collision
        )
        self.add_component(self.__collider)
        controllers.COLLISION_CONTROLLER.add_collider(self.__collider)
        ################################
        ################################

    def on_collision(self, tags: list[str], collider_id: int, entered: bool) -> None:
        if self.__on_collision is not None:
            self.__on_collision(tags, collider_id, entered)

    def delete(self) -> None:
        controllers.COLLISION_CONTROLLER.remove_collider(self.__collider)
        self.__collider.delete()

        super().delete()

    def trigger_delete(self) -> None:
        if self.__on_deletion is not None:
            self.__on_deletion()

    def set_animation(self, animation: Animation) -> None:
        self.__sprite.set_image(animation.content)

    def compute_move_speed(
        self,
        dt: float,
        max_speed: float | None = None,
    ) -> None:
        target_speed: float = 0.0
        target_heading: float = self.move_vec.heading()

        current_speed: float = self.move_vec.length()

        if self.move_vec.length() < target_speed:
            # Accelerate when the current speed is lower than the target speed.
            current_speed += self.move_accel * dt
        else:
            # Decelerate otherwise.
            current_speed -= self.move_accel * dt

        self.move_vec = pm.Vec2.from_polar(
            length = pm.clamp(
                current_speed,
                0.0,
                (max_speed if max_speed is not None else self.max_move_speed)
            ),
            angle = target_heading
        )

    def compute_gravity_speed(self, dt: float) -> None:
        if self.grounded:
            return

        if self.gravity_vec.length() < self.target_gravity_speed:
            # Accelerate when not grounded.
            self.gravity_vec += self.gravity_accel * dt
        elif self.gravity_vec.length() > self.target_gravity_speed:
            # Gravity dampening is not applied during deceleration, in order to allow deceleration also when gravity dampening is 0.
            self.gravity_vec -= self.gravity_accel * dt

            # Make sure to stop at 0.0.
            if self.gravity_vec.y > 0.0:
                self.gravity_vec *= 0.0

        self.gravity_vec = pm.Vec2.from_polar(
            length = round(self.gravity_vec.length(), GLOBALS[Keys.FLOAT_ROUNDING]),
            angle = self.gravity_vec.heading()
        )

    def move(self, dt: float) -> None:
        # Apply movement after collision.
        self.set_position(self.__collider.get_position())

        # Sum movement with gravity.
        velocity: pm.Vec2 = self.move_vec + self.gravity_vec

        if velocity.length() > 0.0:
            self.heading = velocity.heading()

        # Compute and apply velocity for the next step.
        self.set_velocity(velocity = velocity)

    def set_velocity(self, velocity: pyglet.math.Vec2) -> None:
        # Apply the computed velocity to all colliders.
        converted_velocity: tuple[float, float] = (
            round(velocity.x, GLOBALS[Keys.FLOAT_ROUNDING]),
            round(velocity.y, GLOBALS[Keys.FLOAT_ROUNDING])
        )
        self.__collider.set_velocity(converted_velocity)

    def set_shoot_vec(self, shoot_vec: pm.Vec2) -> None:
        """
        Sets the ink's shoot vector.
        """

        self.shoot_vec = shoot_vec