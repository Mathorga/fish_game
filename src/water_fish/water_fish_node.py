from enum import Enum
import math
import pyglet
import pyglet.math as pm
import amonite.controllers as controllers
from amonite.node import PositionNode
from amonite.sprite_node import SpriteNode
from amonite.animation import Animation
from amonite.state_machine import StateMachine
from amonite.state_machine import State
from amonite.collision.collision_node import CollisionNode
from amonite.collision.collision_node import CollisionType
from amonite.collision.collision_shape import CollisionRect
from amonite.settings import SETTINGS
from amonite.settings import GLOBALS
from amonite.settings import Keys
from constants import uniques
from constants import collision_tags

class WaterFishStates(str, Enum):
    IDLE = "idle"
    SWIM = "swim"
    DASH = "dash"

class WaterFishNode(PositionNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        batch: pyglet.graphics.Batch | None = None
    ) -> None:
        super().__init__(x, y, z)

        self.__batch: pyglet.graphics.Batch | None = batch
        self.speed: float = 0.0
        self.max_speed: float = 80.0
        self.accel: float = 150.0
        self.__move_dir: float = 0.0
        self.__hor_facing: int = 1

        ################ Sprite ################
        self.sprite: SpriteNode = SpriteNode(
            resource = Animation(source = "sprites/fish_swim.json").content,
            x = SETTINGS[Keys.VIEW_WIDTH] / 2,
            y = SETTINGS[Keys.VIEW_HEIGHT] / 2,
            on_animation_end = self.on_sprite_animation_end,
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

        ################ State machine ################
        self.__state_machine: StateMachine = StateMachine(
            states = {
                WaterFishStates.IDLE: WaterFishIdleState(actor = self),
                WaterFishStates.SWIM: WaterFishSwimState(actor = self),
                WaterFishStates.DASH: WaterFishDashState(actor = self)
            }
        )

        ################ Inputs ################
        self.__move_vec: pyglet.math.Vec2 = pyglet.math.Vec2()

    def update(self, dt: float) -> None:
        super().update(dt = dt)
        
        self.__state_machine.update(dt = dt)

        # Only update facing if there's any horizontal movement.
        dir_cos: float = math.cos(self.__move_dir)
        dir_len: float = abs(dir_cos)
        if dir_len > 0.1:
            self.__hor_facing = int(math.copysign(1.0, dir_cos))

        # Update sprite position.
        self.sprite.set_position(self.get_position())

        # Flip sprite if moving to the left.
        self.sprite.set_scale(x_scale = self.__hor_facing)

    def set_animation(self, animation: Animation) -> None:
        self.sprite.set_image(animation.content)

    def get_input_movement(self) -> bool:
        return controllers.INPUT_CONTROLLER.get_movement()

    def get_input_movement_vec(self) -> pm.Vec2:
        return controllers.INPUT_CONTROLLER.get_movement_vec()

    def get_input_dash(self) -> bool:
        return controllers.INPUT_CONTROLLER.get_sprint()

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

    def on_sprite_animation_end(self):
        self.__state_machine.on_animation_end()

    def __set_velocity(self, velocity: pyglet.math.Vec2) -> None:
        # Apply the computed velocity to all colliders.
        self.__collider.set_velocity((
            round(velocity.x, GLOBALS[Keys.FLOAT_ROUNDING]),
            round(velocity.y, GLOBALS[Keys.FLOAT_ROUNDING])
        ))

class WaterFishState(State):
    def __init__(
        self,
        actor: WaterFishNode
    ) -> None:
        super().__init__()

        self.input_enabled: bool = True
        self.actor: WaterFishNode = actor

    def enable_input(self) -> None:
        """
        Enables all input reading.
        """

        self.input_enabled = True

    def disable_input(self) -> None:
        """
        Disables all input reading.
        """

        self.input_enabled = False

class WaterFishIdleState(WaterFishState):
    def __init__(
        self,
        actor: WaterFishNode
    ) -> None:
        super().__init__(actor = actor)

        self.__animation: Animation = Animation(source = "sprites/fish_idle.json")

        # Inputs.
        self.__move: bool = False
        self.__dash: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move = self.actor.get_input_movement()
            self.__dash = self.actor.get_input_dash()

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        # Check for state changes.
        if self.__move:
            return WaterFishStates.SWIM

        if self.__dash:
            return WaterFishStates.DASH

class WaterFishSwimState(WaterFishState):
    def __init__(
        self,
        actor: WaterFishNode
    ) -> None:
        super().__init__(actor = actor)

        # Animation.
        self.__animation: Animation = Animation(source = "sprites/fish_swim.json")

        # Input.
        self.__move_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__dash: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move_vec = self.actor.get_input_movement_vec()
            self.__dash = self.actor.get_input_dash()

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        self.actor.compute_speed(move_vec = self.__move_vec, dt = dt)

        # Move the player.
        self.actor.move(dt = dt)

        # Check for state changes.
        if self.__dash:
            return WaterFishStates.DASH

        if self.actor.speed <= 0.0:
            return WaterFishStates.IDLE

class WaterFishDashState(WaterFishState):
    def __init__(
        self,
        actor: WaterFishNode
    ) -> None:
        super().__init__(actor = actor)

        # Animation.
        self.__animation: Animation = Animation(source = "sprites/fish_dash.json")
        self.__startup: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.__startup = True

    def update(self, dt: float) -> str | None:
        if self.__startup:
            self.actor.speed = self.actor.max_speed * 2
            self.__startup = False
        else:
            self.actor.speed -= (self.actor.accel / 2) * dt

        # Move the player.
        self.actor.move(dt = dt)

        # Check for state changes.
        if self.actor.speed <= 0.0:
            return WaterFishStates.IDLE

    def on_animation_end(self) -> str | None:
        if self.actor.speed <= 0.0:
            return WaterFishStates.IDLE
        else:
            return WaterFishStates.SWIM