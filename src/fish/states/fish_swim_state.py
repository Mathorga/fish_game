import pyglet

from amonite.settings import SETTINGS
from amonite.settings import Keys
from amonite.animation import Animation
import amonite.controllers as controllers
from amonite.input_controller import ControllerButton
from amonite.input_controller import ControllerStick

from constants import custom_setting_keys
from constants import uniques
from fish.fish_data_node import FishDataNode
from fish.states.fish_state import FishState
from fish.states.fish_state import FishStates

class FishSwimState(FishState):
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
        self.__animation: Animation = Animation(source = "sprites/fish/dumbo_swim.json")

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
            self.__move_vec = controllers.INPUT_CONTROLLER.get_stick_vector(
                stick = ControllerStick.LSTICK,
                controller_index = uniques.FISH_CONTROLLER
            )
            self.__dash = controllers.INPUT_CONTROLLER.get_button_presses(
                button = ControllerButton.SOUTH,
                controller_index = uniques.FISH_CONTROLLER
            )

            # Only read keyboard input if so specified in settings.
            if SETTINGS[Keys.DEBUG] and SETTINGS[custom_setting_keys.KEYBOARD_CONTROLS]:
                self.__move_vec += controllers.INPUT_CONTROLLER.get_key_vector()
                self.__dash = self.__dash or controllers.INPUT_CONTROLLER.key_presses.get(pyglet.window.key.SPACE, False)

            self.__move_vec = self.__move_vec.normalize()

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        self.actor.compute_move_speed(move_vec = self.__move_vec, dt = dt)
        self.actor.compute_gravity_speed(dt = dt)

        # Move the player.
        self.actor.move(dt = dt)

        # Check for state changes.
        if not self.actor.in_water:
            return FishStates.IDLE if self.__move_vec.length() <= 0.0 else FishStates.CRAWL

        if self.__dash:
            return FishStates.DASH