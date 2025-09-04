from amonite.input_controller import ControllerButton, ControllerStick
import pyglet
import pyglet.math as pm

from amonite.settings import SETTINGS
from amonite.settings import Keys
from amonite.animation import Animation
import amonite.controllers as controllers

from constants import custom_setting_keys
from constants import uniques
from leg.leg_data_node import LegDataNode
from leg.states.leg_state import LegStates
from leg.states.leg_state import LegState

class LegWalkState(LegState):
    def __init__(
        self,
        actor: LegDataNode,
        input_enabled: bool = True
    ) -> None:
        super().__init__(
            actor = actor,
            input_enabled = input_enabled
        )

        # Animation.
        self.__animation: Animation = Animation(source = "sprites/leg/leg_walk.json")

        # Input.
        self.__move_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__jump: bool = False
        self.__grab: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move_vec = controllers.INPUT_CONTROLLER.get_stick_vector(
                stick = ControllerStick.LSTICK,
                controller_index = uniques.LEG_CONTROLLER
            )
            self.__jump = controllers.INPUT_CONTROLLER.get_button(
                button = ControllerButton.SOUTH,
                controller_index = uniques.LEG_CONTROLLER
            )
            self.__grab = controllers.INPUT_CONTROLLER.get_button_presses(
                button = ControllerButton.WEST,
                controller_index = uniques.LEG_CONTROLLER
            )

            # Only read keyboard input if so specified in settings.
            if SETTINGS[custom_setting_keys.KEYBOARD_CONTROLS]:
                self.__move_vec += controllers.INPUT_CONTROLLER.get_key_vector()
                self.__jump += controllers.INPUT_CONTROLLER[pyglet.window.key.SPACE]
                self.__grab += controllers.INPUT_CONTROLLER.key_presses.get(pyglet.window.key.H, False)

            self.__move_vec = self.__move_vec.normalize()

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        if self.__grab:
            self.actor.toggle_grab()

        self.actor.compute_move_speed(dt = dt, move_vec = pm.Vec2(self.__move_vec.x, 0.0))
        self.actor.compute_gravity_speed(dt = dt)

        # Move the player.
        self.actor.move(dt = dt)

        # Check for state changes.
        if self.__jump and self.actor.grounded:
            return LegStates.JUMP_LOAD

        if self.actor.move_vec.length() <= 0.0:
            return LegStates.IDLE