import pyglet
import pyglet.math as pm

from amonite.animation import Animation
import amonite.controllers as controllers
from amonite.input_controller import ControllerButton
from amonite.input_controller import ControllerStick

from constants import uniques
from leg.leg_data_node import LegDataNode
from leg.states.leg_state import LegStates
from leg.states.leg_state import LegState

class LegIdleState(LegState):
    def __init__(
        self,
        actor: LegDataNode,
        input_enabled: bool = True
    ) -> None:
        super().__init__(
            actor = actor,
            input_enabled = input_enabled
        )

        self.__animation: Animation = Animation(source = "sprites/leg/leg_idle.json")

        # Inputs.
        self.__move: bool = False
        self.__jump: bool = False
        self.__grab: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move = (
                controllers.INPUT_CONTROLLER.get_stick_vector(
                    stick = ControllerStick.LSTICK
                ) + controllers.INPUT_CONTROLLER.get_key_vector()
            ).normalize().length() > 0.0
            self.__jump = controllers.INPUT_CONTROLLER[pyglet.window.key.SPACE] or controllers.INPUT_CONTROLLER.get_button(
                button = ControllerButton.DOWN,
                controller_index = uniques.LEG_CONTROLLER
            )
            self.__grab = controllers.INPUT_CONTROLLER.key_presses.get(pyglet.window.key.H, False) or controllers.INPUT_CONTROLLER.get_button_presses(
                button = ControllerButton.WEST,
                controller_index = uniques.LEG_CONTROLLER
            )

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        if self.__grab:
            self.actor.toggle_grab()

        self.actor.compute_move_speed(dt = dt, move_vec = pm.Vec2(0.0, 0.0))
        self.actor.compute_gravity_speed(dt = dt)

        self.actor.move(dt = dt)

        # Check for state changes.
        if self.__move:
            return LegStates.WALK

        if self.__jump and self.actor.grounded:
            return LegStates.JUMP_LOAD