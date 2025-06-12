import pyglet
import pyglet.math as pm

from amonite.animation import Animation
import amonite.controllers as controllers
from amonite.input_controller import ControllerStick

from constants import uniques
from fish.fish_data_node import FishDataNode
from fish.states.fish_state import FishState
from fish.states.fish_state import FishStates

class FishCrawlState(FishState):
    def __init__(
        self,
        actor: FishDataNode,
        input_enabled: bool = True
    ) -> None:
        super().__init__(
            actor = actor,
            input_enabled = input_enabled
        )

        # Animation.
        self.__animation: Animation = Animation(source = "sprites/fish/dumbo_land_idle.json")

        # Input.
        self.__move_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__aim_vec: pyglet.math.Vec2 = pyglet.math.Vec2()

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move_vec = controllers.INPUT_CONTROLLER.get_movement_vec(
                controller_index = uniques.FISH_CONTROLLER
            )
            self.__aim_vec = (
                controllers.INPUT_CONTROLLER.get_stick_vector(
                    stick = ControllerStick.RSTICK,
                    controller_index = uniques.FISH_CONTROLLER
                ) +
                controllers.INPUT_CONTROLLER.get_key_vector(
                    up = pyglet.window.key.I,
                    left = pyglet.window.key.J,
                    down = pyglet.window.key.K,
                    right = pyglet.window.key.L
                )
            ).normalize()

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        self.actor.compute_move_speed(
            move_vec = pm.Vec2(self.__move_vec.x, 0.0),
            dt = dt
        )
        self.actor.compute_gravity_speed(dt = dt)

        # Move the player.
        self.actor.move(dt = dt)

        # Check for state transitions.
        if self.actor.in_water:
            return FishStates.SWIM
        
        if self.__aim_vec.length() > 0.0:
            self.actor.aim_vec = self.__aim_vec
            return FishStates.SHOOT_LOAD

        if self.actor.move_vec.length() <= 0.0:
            return FishStates.IDLE