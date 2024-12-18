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
from amonite.collision.collision_node import CollisionMethod
from amonite.settings import SETTINGS
from amonite.settings import GLOBALS
from amonite.settings import Keys

from constants import collision_tags


class FishDataNode(PositionNode):
    """
    """

    # __slots__ = (
    #     "__batch",
    #     "speed",
    #     "max_speed",
    #     "accel",
    #     "__move_dir",
    #     "__hor_facing",
    #     "sprite",
    #     "__collider"
    # )
    water_dampening: float = 1.0
    land_dampening: float = 0.5

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        on_sprite_animation_end: Callable | None = None,
        batch: pyglet.graphics.Batch | None = None
    ) -> None:
        super().__init__(x, y, z)

        self.__batch: pyglet.graphics.Batch | None = batch
        self.__hor_facing: int = 1


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
        self.target_gravity_speed: float = math.inf
        self.gravity_accel: pm.Vec2 = pm.Vec2(0.0, -1200.0)
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


        self.dash_force: float = self.max_move_speed * 5


        ################################
        # Sprite
        ################################
        self.sprite: SpriteNode = SpriteNode(
            resource = Animation(source = "sprites/fish/dumbo_swim.json").content,
            x = SETTINGS[Keys.VIEW_WIDTH] / 2,
            y = SETTINGS[Keys.VIEW_HEIGHT] / 2,
            y_sort = False,
            on_animation_end = on_sprite_animation_end,
            batch = batch
        )
        ################################
        ################################


        ################################
        # Collider
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
            passive_tags = [
            ],
            shape = CollisionRect(
                x = x,
                y = y,
                anchor_x = 5,
                anchor_y = 7,
                width = 10,
                height = 14,
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
                anchor_x = 5,
                anchor_y = 8,
                width = 10,
                height = 2,
                batch = batch
            ),
            on_triggered = self.on_ground_collision
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.__collider)
        controllers.COLLISION_CONTROLLER.add_collider(self.__ground_sensor)
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
            self.target_gravity_speed = 0.0
        else:
            self.target_gravity_speed = math.inf

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

    def get_move_dampening(self) -> float:
        return self.water_dampening if self.in_water else self.land_dampening

    def get_gravity_dampening(self) -> float:
        return 0.0 if self.in_water else self.water_dampening

    def update(self, dt: float) -> None:
        super().update(dt = dt)

        # Only update facing if there's any horizontal movement.
        dir_cos: float = math.cos(self.move_vec.heading)
        dir_len: float = abs(dir_cos)
        if dir_len > 0.1:
            self.__hor_facing = int(math.copysign(1.0, dir_cos))

        # Update sprite position.
        self.sprite.set_position(self.get_position())

        # Update colliders positions.
        self.__ground_sensor.set_position(self.get_position())

        # Flip sprite if moving to the left.
        self.sprite.set_scale(x_scale = self.__hor_facing)

    def delete(self) -> None:
        self.sprite.delete()
        self.__collider.delete()
        super().delete()

    def set_animation(self, animation: Animation) -> None:
        self.sprite.set_image(animation.content)

    def compute_move_speed(
        self,
        move_vec: pyglet.math.Vec2,
        dt: float,
        max_speed: float | None = None,
    ) -> None:
        target_speed: float = 0.0
        target_heading: float = self.move_vec.heading

        current_speed: float = self.move_vec.mag

        if move_vec.mag > 0.0:
            target_speed = self.max_move_speed
            target_heading = move_vec.heading

        if move_vec.mag < target_speed:
            # Accelerate when the current speed is lower than the target speed.
            current_speed += self.move_accel * self.get_move_dampening() * dt
        else:
            # Decelerate otherwise.
            current_speed -= self.move_accel * self.get_move_dampening() * dt

        self.move_vec = pm.Vec2.from_polar(
            pm.clamp(
                current_speed,
                0.0,
                (max_speed if max_speed is not None else self.max_move_speed) * self.get_move_dampening()
            ),
            target_heading
        )

    def compute_gravity_speed(self, dt: float) -> None:
        if self.grounded:
            return

        if self.gravity_vec.mag < self.target_gravity_speed:
            # Accelerate when not grounded.
            self.gravity_vec += self.gravity_accel * self.get_gravity_dampening() * dt
        elif self.gravity_vec.mag > self.target_gravity_speed:
            self.gravity_vec -= self.gravity_accel * dt

        self.gravity_vec = pm.Vec2.from_polar(
            round(self.gravity_vec.mag, GLOBALS[Keys.FLOAT_ROUNDING]),
            self.gravity_vec.heading
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