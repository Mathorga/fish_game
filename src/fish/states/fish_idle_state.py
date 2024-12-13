import pyglet.math as pm

from amonite.animation import Animation
import amonite.controllers as controllers

from fish.fish_data_node import FishDataNode
from fish.states.fish_state import FishStates
from fish.states.fish_state import FishState

class FishIdleState(FishState):
    def __init__(
        self,
        actor: FishDataNode
    ) -> None:
        super().__init__(actor = actor)

        self.__water_animation: Animation = Animation(source = "sprites/fish/dumbo_water_idle.json")
        self.__land_animation: Animation = Animation(source = "sprites/fish/dumbo_land_idle.json")

        # Inputs.
        self.__move: bool = False
        self.__dash: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__water_animation if self.actor.in_water else self.__land_animation)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move = controllers.INPUT_CONTROLLER.get_movement(controller_index = 1)
            self.__dash = controllers.INPUT_CONTROLLER.get_sprint(controller_index = 1)

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        self.actor.compute_move_speed(dt = dt, move_vec = pm.Vec2(0.0, 0.0))
        self.actor.compute_gravity_speed(dt = dt)

        self.actor.move(dt = dt)

        # Check for state changes.
        if self.__move:
            return FishStates.SWIM if self.actor.in_water else FishStates.CRAWL

        if self.__dash:
            return FishStates.DASH