import math
import pyglet
import pyglet.math as pm
from amonite.node import PositionNode
from amonite.sprite_node import SpriteNode
from amonite.animation import Animation
from amonite.collision.collision_node import CollisionNode
from amonite.collision.collision_node import CollisionType
from amonite.collision.collision_shape import CollisionRect
import amonite.controllers as controllers
from amonite.settings import SETTINGS
from amonite.settings import GLOBALS
from amonite.settings import Keys
from constants import uniques
from constants import collision_tags

class FishNode(PositionNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        batch: pyglet.graphics.Batch | None = None
    ) -> None:
        super().__init__(x, y, z)

        self.__batch: pyglet.graphics.Batch | None = batch
        self.__speed: float = 0.0
        self.__max_speed: float = 100.0
        self.__accel: float = 150.0
        self.__move_dir: float = 0.0
        self.__hor_facing: int = 1

        ################ Animations ################
        self.__idle_animation: Animation = Animation(source = "sprites/fish_idle.json")

        ################ Sprite ################
        self.__sprite: SpriteNode = SpriteNode(
            resource = self.__idle_animation.content,
            x = SETTINGS[Keys.VIEW_WIDTH] / 2,
            y = SETTINGS[Keys.VIEW_HEIGHT] / 2,
            batch = batch
        )

        ################ Collider ################
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
                collision_tags.DAMAGE
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

        ################ Inputs ################
        self.__move_vec: pyglet.math.Vec2 = pyglet.math.Vec2()

    def update(self, dt: float) -> None:
        super().update(dt)

        # Read inputs.
        self.__fetch_input()

        # Compute speed and then move.
        self.__compute_speed(dt = dt)

        self.move(dt = dt)

        # Only update facing if there's any horizontal movement.
        dir_cos: float = math.cos(self.__move_dir)
        dir_len: float = abs(dir_cos)
        if dir_len > 0.1:
            self.__hor_facing = int(math.copysign(1.0, dir_cos))

        # Update sprite position.
        self.__sprite.set_position(self.get_position())

        # Flip sprite if moving to the left.
        self.__sprite.set_scale(x_scale = self.__hor_facing)

    def __compute_speed(self, dt: float) -> None:
        target_speed: float = 0.0
        if self.__move_vec.mag > 0.0:
            # Only set dirs if there's any move input.
            self.__move_dir = self.__move_vec.heading

            target_speed = self.__max_speed

        if self.__speed < target_speed:
            # Accelerate when the current speed is lower than the target speed.
            self.__speed += self.__accel * dt
        else:
            # Decelerate otherwise.
            self.__speed -= self.__accel * dt
        self.__speed = pm.clamp(self.__speed, 0.0, self.__max_speed)

    def __fetch_input(self) -> None:
        self.__move_vec = controllers.INPUT_CONTROLLER.get_movement_vec()

    def move(self, dt: float) -> None:
        # Apply movement after collision.
        self.set_position(self.__collider.get_position())

        # Compute velocity.
        velocity: pyglet.math.Vec2 = pm.Vec2.from_polar(self.__speed, self.__move_dir)

        self.__set_velocity(velocity = velocity)

    def __set_velocity(self, velocity: pyglet.math.Vec2) -> None:
        # Apply the computed velocity to all colliders.
        self.__collider.set_velocity((
            round(velocity.x, GLOBALS[Keys.FLOAT_ROUNDING]),
            round(velocity.y, GLOBALS[Keys.FLOAT_ROUNDING])
        ))