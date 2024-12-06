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


class WaterFishDataNode(PositionNode):
    """
    """

    __slots__ = (
        "__batch",
        "speed",
        "max_speed",
        "accel",
        "__move_dir",
        "__hor_facing",
        "sprite",
        "__collider"
    )

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
        self.speed: float = 0.0
        self.max_speed: float = 80.0
        self.accel: float = 200.0
        self.__move_dir: float = 0.0
        self.__hor_facing: int = 1


        ################################
        # Sprite
        ################################
        self.sprite: SpriteNode = SpriteNode(
            resource = Animation(source = "sprites/fish/water_fish/water_fish_swim.json").content,
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
                collision_tags.FALL
            ],
            passive_tags = [
            ],
            shape = CollisionRect(
                x = x,
                y = y,
                anchor_x = 3,
                anchor_y = 3,
                width = 6,
                height = 6,
                batch = batch
            )
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.__collider)
        ################################
        ################################

    def update(self, dt: float) -> None:
        super().update(dt = dt)

        # Only update facing if there's any horizontal movement.
        dir_cos: float = math.cos(self.__move_dir)
        dir_len: float = abs(dir_cos)
        if dir_len > 0.1:
            self.__hor_facing = int(math.copysign(1.0, dir_cos))

        # Update sprite position.
        self.sprite.set_position(self.get_position())

        # Flip sprite if moving to the left.
        self.sprite.set_scale(x_scale = self.__hor_facing)

    def delete(self) -> None:
        self.sprite.delete()
        self.__collider.delete()
        super().delete()

    def set_animation(self, animation: Animation) -> None:
        self.sprite.set_image(animation.content)

    def compute_speed(self, move_vec: pyglet.math.Vec2, dt: float) -> None:
        target_speed: float = 0.0
        if move_vec.mag > 0.0:
            # Only set dirs if there's any move input.
            self.__move_dir = move_vec.heading

            target_speed = self.max_speed

        if self.speed < target_speed:
            # Accelerate when the current speed is lower than the target speed.
            self.speed += self.accel * dt
        else:
            # Decelerate otherwise.
            self.speed -= self.accel * dt
        self.speed = pm.clamp(self.speed, 0.0, self.max_speed)

    def move(self, dt: float) -> None:
        # Apply movement after collision.
        self.set_position(self.__collider.get_position())

        # Compute velocity.
        velocity: pyglet.math.Vec2 = pm.Vec2.from_polar(self.speed, self.__move_dir)

        self.__set_velocity(velocity = velocity)

    def __set_velocity(self, velocity: pyglet.math.Vec2) -> None:
        # Apply the computed velocity to all colliders.
        self.__collider.set_velocity((
            round(velocity.x, GLOBALS[Keys.FLOAT_ROUNDING]),
            round(velocity.y, GLOBALS[Keys.FLOAT_ROUNDING])
        ))