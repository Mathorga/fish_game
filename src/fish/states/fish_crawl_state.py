import pyglet
import pyglet.math as pm

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
        self.__land_animation: Animation = Animation(source = "sprites/fish/dumbo_land_idle.json")
        self.__midair_animation: Animation = Animation(source = "sprites/fish/dumbo_swim.json")
        self.__animation: Animation = self.__land_animation if self.actor.grounded else self.__midair_animation

        # Input.
        self.__move_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__aim: bool = False
        self.__interact: bool = False

    def __update_animation(self) -> None:
        if self.actor.grounded and self.__animation != self.__land_animation:
            self.__animation = self.__land_animation
            self.actor.set_animation(self.__animation)
            return

        if not self.actor.grounded and self.__animation != self.__midair_animation:
            self.__animation = self.__midair_animation
            self.actor.set_animation(self.__animation)
            return

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.__update_animation()

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move_vec = controllers.INPUT_CONTROLLER.get_stick_vector(
                stick = ControllerStick.LSTICK,
                controller_index = uniques.FISH_CONTROLLER
            )
            self.__aim = controllers.INPUT_CONTROLLER.get_button_presses(
                button = ControllerButton.EAST,
                controller_index = uniques.FISH_CONTROLLER
            )
            self.__interact = controllers.INPUT_CONTROLLER.get_button_presses(
                button = ControllerButton.WEST,
                controller_index = uniques.FISH_CONTROLLER
            )

            # Only read keyboard input if so specified in settings.
            if SETTINGS[custom_setting_keys.KEYBOARD_CONTROLS]:
                self.__move_vec = controllers.INPUT_CONTROLLER.get_key_vector()
                self.__aim = self.__aim or controllers.INPUT_CONTROLLER.key_presses.get(pyglet.window.key.RSHIFT, False)
                self.__interact = self.__interact or controllers.INPUT_CONTROLLER.key_presses.get(pyglet.window.key.H, False)

            self.__move_vec = self.__move_vec.normalize()
        else:
            self.__move_vec = pm.Vec2()
            self.__aim = False
            self.__interact = False

    def update(self, dt: float) -> str | None:
        self.__update_animation()

        # Read inputs.
        self.__fetch_input()

        if self.__interact:
            self.actor.interact()

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
        
        if self.__aim:
            return FishStates.SHOOT_LOAD

        if self.actor.move_vec.length() <= 0.0:
            return FishStates.IDLE