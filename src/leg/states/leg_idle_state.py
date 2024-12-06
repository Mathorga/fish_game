from amonite.input_controller import ControllerButton, ControllerStick
import pyglet
import pyglet.math as pm

from amonite.animation import Animation
import amonite.controllers as controllers

from constants import collision_tags
from leg.leg_data_node import LegDataNode
from leg.states.leg_state import LegStates
from leg.states.leg_state import LegState

class LegIdleState(LegState):
    def __init__(
        self,
        actor: LegDataNode
    ) -> None:
        super().__init__(actor = actor)

        self.__animation: Animation = Animation(source = "sprites/leg/leg_idle.json")

        # Inputs.
        self.__move: bool = False
        self.__jump: bool = False

        # Other.
        self.__in_water: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.actor.dampening = 1.0
        self.__in_water = False

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move = (controllers.INPUT_CONTROLLER.get_stick_vector(ControllerStick.LSTICK) + controllers.INPUT_CONTROLLER.get_key_vector()).normalize().mag > 0.0
            self.__jump = controllers.INPUT_CONTROLLER[pyglet.window.key.SPACE] or controllers.INPUT_CONTROLLER.get_button(ControllerButton.DOWN)

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        self.actor.compute_move_speed(dt = dt, move_vec = pm.Vec2(0.0, 0.0))
        self.actor.compute_gravity_speed(dt = dt)

        self.actor.move(dt = dt)

        # Check for state changes.
        if self.__in_water:
            return LegStates.WATER_IDLE

        if self.__move:
            return LegStates.WALK

        if self.__jump and self.actor.grounded:
            return LegStates.JUMP_LOAD

    def on_collision(self, tags: list[str], enter: bool) -> None:
        super().on_collision(tags, enter)

        if enter and collision_tags.WATER:
            self.__in_water = True