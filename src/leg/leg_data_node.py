import math
import time
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
from amonite.collision.collision_node import CollisionMethod
from amonite.settings import SETTINGS
from amonite.settings import GLOBALS
from amonite.settings import Keys

from constants import collision_tags

class LegDataNode(PositionNode):
    """
    """

    __slots__ = (
        "__on_collision",
        "__batch",
        "move_vec",
        "max_move_speed",
        "move_accel",
        "gravity_vec",
        "max_gravity_speed",
        "gravity_accel",
        "__ground_collision_ids",
        "__roof_collision_ids",
        "__water_collision_ids",
        "grounded",
        "roofed",
        "in_water",
        "__hor_facing",
        "jump_force",
        "sprite",
        "__collider",
        "__ground_sensor",
        "__roof_sensor"
    )
    water_dampening: float = 0.5
    land_dampening: float = 1.0
    max_jump_force: float = 500.0

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        on_sprite_animation_end: Callable | None = None,
        on_collision: Callable | None = None,
        batch: pyglet.graphics.Batch | None = None
    ) -> None:
        super().__init__(x, y, z)

        self.__on_collision: Callable | None = on_collision
        self.__batch: pyglet.graphics.Batch | None = batch


        ################################
        # Input movement.
        ################################
        self.move_vec: pm.Vec2 = pm.Vec2(0.0, 0.0)
        self.max_move_speed: float = 80.0
        self.move_accel: float = 400.0
        ################################
        ################################


        ################################
        # Gravity movement.
        ################################
        self.gravity_vec: pm.Vec2 = pm.Vec2(0.0, 0.0)
        self.gravity_accel: pm.Vec2 = pm.Vec2(0.0, -1200.0)
        ################################
        ################################


        ################################
        # Collision flags.
        ################################
        self.__ground_collision_ids: set[int] = set()
        self.__roof_collision_ids: set[int] = set()
        self.__water_collision_ids: set[int] = set()
        self.grounded: bool = False
        self.roofed: bool = False
        self.in_water: bool = False
        ################################
        ################################


        self.__hor_facing: int = 1
        self.jump_force: float = 0.0


        ################################
        # Sprite.
        ################################
        self.sprite: SpriteNode = SpriteNode(
            resource = Animation(source = "sprites/leg/leg_idle.json").content,
            x = SETTINGS[Keys.VIEW_WIDTH] / 2,
            y = SETTINGS[Keys.VIEW_HEIGHT] / 2,
            y_sort = False,
            on_animation_end = on_sprite_animation_end,
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
            collision_type = CollisionType.DYNAMIC,
            active_tags = [
                collision_tags.PLAYER_COLLISION,
                collision_tags.PLAYER_SENSE,
                collision_tags.FALL,
                collision_tags.WATER
            ],
            passive_tags = [],
            shape = CollisionRect(
                x = x,
                y = y,
                anchor_x = 6,
                anchor_y = 16,
                width = 12,
                height = 28,
                batch = batch
            ),
            on_triggered = self.on_collision
        )
        self.__ground_sensor: CollisionNode = CollisionNode(
            x = x,
            y = y,
            collision_type = CollisionType.DYNAMIC,
            collision_method = CollisionMethod.PASSIVE,
            sensor = True,
            active_tags = [
                collision_tags.PLAYER_COLLISION
            ],
            passive_tags = [],
            shape = CollisionRect(
                x = x,
                y = y,
                anchor_x = 6,
                anchor_y = 17,
                width = 12,
                height = 2,
                batch = batch
            ),
            on_triggered = self.on_ground_collision
        )
        self.__roof_sensor: CollisionNode = CollisionNode(
            x = x,
            y = y,
            collision_type = CollisionType.DYNAMIC,
            collision_method = CollisionMethod.PASSIVE,
            sensor = True,
            active_tags = [
                collision_tags.PLAYER_COLLISION
            ],
            passive_tags = [],
            shape = CollisionRect(
                x = x,
                y = y,
                anchor_x = 6,
                anchor_y = -11,
                width = 12,
                height = 2,
                batch = batch
            ),
            on_triggered = self.on_roof_collision
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.__collider)
        controllers.COLLISION_CONTROLLER.add_collider(self.__ground_sensor)
        controllers.COLLISION_CONTROLLER.add_collider(self.__roof_sensor)
        ################################
        ################################

    def on_collision(self, tags: list[str], collider_id: int, entered: bool) -> None:
        if not collision_tags.WATER in tags:
            return

        if entered:
            self.in_water = True
        else:
            self.in_water = False

        # Clear gravity vector on collision.
        if self.in_water:
            self.gravity_vec *= 0.0

    def on_ground_collision(self, tags: list[str], collider_id: int, entered: bool) -> None:
        if entered:
            self.__ground_collision_ids.add(collider_id)
        else:
            if collider_id in self.__ground_collision_ids:
                self.__ground_collision_ids.remove(collider_id)

        if len(self.__ground_collision_ids) > 0:
            self.grounded = True
        else:
            self.grounded = False

        # Clear gravity vector on collision.
        if self.grounded:
            self.gravity_vec *= 0.0

    def on_roof_collision(self, tags: list[str], collider_id: int, entered: bool) -> None:
        if entered:
            self.__roof_collision_ids.add(collider_id)
        else:
            if collider_id in self.__roof_collision_ids:
                self.__roof_collision_ids.remove(collider_id)

        if len(self.__roof_collision_ids) > 0:
            self.roofed = True
        else:
            self.roofed = False

        # Clear gravity vector on collision.
        if self.roofed:
            self.gravity_vec *= 0.0
            self.roofed = False

    def get_dampening(self) -> float:
        return self.water_dampening if self.in_water else self.land_dampening

    def get_max_jump_force(self) -> float:
        return self.max_jump_force * self.get_dampening()

    def update(self, dt: float) -> None:
        super().update(dt = dt)

        # Only update facing if there's any horizontal movement.
        dir_cos: float = math.cos(self.move_vec.heading())
        dir_len: float = abs(dir_cos)
        if dir_len > 0.1:
            self.__hor_facing = int(math.copysign(1.0, dir_cos))

        # Update sprite position.
        self.sprite.set_position(self.get_position())

        # Update sensors position
        # self.__water_sensor.set_position(self.get_position())
        self.__ground_sensor.set_position(self.get_position())
        self.__roof_sensor.set_position(self.get_position())

        # Flip sprite if moving to the left.
        self.sprite.set_scale(x_scale = self.__hor_facing)

    def delete(self) -> None:
        self.sprite.delete()
        self.__collider.delete()
        super().delete()

    def set_animation(self, animation: Animation) -> None:
        self.sprite.set_image(animation.content)

    def compute_move_speed(self, move_vec: pyglet.math.Vec2, dt: float) -> None:
        target_speed: float = 0.0
        target_heading: float = self.move_vec.heading()

        current_speed: float = self.move_vec.length()

        if move_vec.length() > 0.0:
            target_speed = self.max_move_speed
            target_heading = move_vec.heading()

        if move_vec.length() < target_speed:
            # Accelerate when the current speed is lower than the target speed.
            current_speed += self.move_accel * self.get_dampening() * dt
        else:
            # Decelerate otherwise.
            current_speed -= self.move_accel * self.get_dampening() * dt

        self.move_vec = pm.Vec2.from_polar(
            length = pm.clamp(current_speed, 0.0, self.max_move_speed * self.get_dampening()),
            angle = target_heading
        )

    def compute_gravity_speed(self, dt: float) -> None:
        if self.grounded:
            return

        # Accelerate when not grounded.
        self.gravity_vec += self.gravity_accel * self.get_dampening() * dt

        self.gravity_vec = pm.Vec2.from_polar(
            length = round(self.gravity_vec.length(), GLOBALS[Keys.FLOAT_ROUNDING]),
            angle = self.gravity_vec.heading()
        )

    def move(self, dt: float) -> None:
        # Apply movement after collision.
        self.set_position(self.__collider.get_position())

        # Compute and apply velocity for the next step.
        self.set_velocity(velocity = self.move_vec + self.gravity_vec)

    def set_velocity(self, velocity: pyglet.math.Vec2) -> None:
        # Apply the computed velocity to all colliders.
        converted_velocity: tuple[float, float] = (
            round(velocity.x, GLOBALS[Keys.FLOAT_ROUNDING]),
            round(velocity.y, GLOBALS[Keys.FLOAT_ROUNDING])
        )
        self.__collider.set_velocity(converted_velocity)

    def put_velocity(self, velocity: pyglet.math.Vec2) -> None:
        # Apply the computed velocity to all colliders.
        converted_velocity: tuple[float, float] = (
            round(velocity.x, GLOBALS[Keys.FLOAT_ROUNDING]),
            round(velocity.y, GLOBALS[Keys.FLOAT_ROUNDING])
        )
        self.__collider.put_velocity(converted_velocity)