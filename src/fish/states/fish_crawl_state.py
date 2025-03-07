import pyglet
import pyglet.math as pm

from amonite.animation import Animation
import amonite.controllers as controllers

from fish.fish_data_node import FishDataNode
from fish.states.fish_state import FishState
from fish.states.fish_state import FishStates

class FishCrawlState(FishState):
    def __init__(
        self,
        actor: FishDataNode
    ) -> None:
        super().__init__(actor = actor)

        # Animation.
        self.__animation: Animation = Animation(source = "sprites/fish/dumbo_land_idle.json")

        # Input.
        self.__move_vec: pyglet.math.Vec2 = pyglet.math.Vec2()

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move_vec = controllers.INPUT_CONTROLLER.get_movement_vec(controller_index = 1)

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

        if self.actor.move_vec.length() <= 0.0:
            return FishStates.IDLE