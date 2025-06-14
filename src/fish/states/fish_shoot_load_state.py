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

class FishShootLoadState(FishState):
    def __init__(
        self,
        actor: FishDataNode,
        input_enabled: bool = True
    ) -> None:
        super().__init__(
            actor = actor,
            input_enabled = input_enabled
        )

        ########################
        # Animation.
        ########################
        self.__animation: Animation = Animation(source = "sprites/fish/dumbo_shoot_load.json")
        ########################
        ########################

        ########################
        # Input.
        ########################
        self.__shoot: bool = False
        self.__aim_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        ########################
        ########################

        ########################
        # Other.
        ########################
        # Time elapsed since state start, used to check for releasability.
        self.__elapsed: float = 0.0

        # Time (in seconds) before the player can release the shoot.
        self.__release_threshold: float = 1.0
        self.__animation_ended: bool = False

        self.__shoot_force: float = self.actor.min_shoot_force
        self.__shoot_force_step: float = 200.0
        ########################
        ########################

    def start(self) -> None:
        self.__shoot_force = self.actor.min_shoot_force
        self.__shoot = False
        self.__elapsed = 0.0
        self.__release_threshold = 1.0
        self.__animation_ended = False
        self.actor.set_animation(self.__animation)
        self.actor.move_vec *= 0.0
        self.actor.spawn_ink()
        self.actor.set_shoot_force(self.__shoot_force)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__aim_vec: pm.Vec2 = controllers.INPUT_CONTROLLER.get_stick_vector(
                stick = ControllerStick.RSTICK,
                controller_index = uniques.FISH_CONTROLLER
            )
            self.__shoot = controllers.INPUT_CONTROLLER.get_button_presses(
                button = ControllerButton.SOUTH,
                controller_index = uniques.FISH_CONTROLLER
            )

            # Only read keyboard input if so specified in settings.
            if SETTINGS[Keys.DEBUG] and SETTINGS[custom_setting_keys.KEYBOARD_CONTROLS]:
                self.__aim_vec += controllers.INPUT_CONTROLLER.get_key_vector(
                    up = pyglet.window.key.I,
                    left = pyglet.window.key.J,
                    down = pyglet.window.key.K,
                    right = pyglet.window.key.L
                )
                self.__shoot += controllers.INPUT_CONTROLLER.key_presses.get(pyglet.window.key.SPACE, False)

            self.__aim_vec = self.__aim_vec.normalize()

    def __can_release(self) -> bool:
        return self.__animation_ended or self.__elapsed > self.__release_threshold

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        # Move the aiming around. This should also update the actor's facing.
        self.actor.aim_vec = self.__aim_vec
        self.actor.move_ink()

        self.__elapsed += dt
        self.__shoot_force += self.__shoot_force_step * dt

        # Make sure the shoot force does not exceed its maximum possible value.
        self.__shoot_force = pm.clamp(self.__shoot_force, 0.0, self.actor.max_shoot_force)

        self.actor.set_shoot_force(self.__shoot_force)

        # Check for state changes.
        if self.__shoot and self.__can_release:
            return FishStates.SHOOT

        if self.__aim_vec.length() <= 0.0:
            # Make sure the ink is deleted if back to idle.
            self.actor.delete_ink()
            return FishStates.IDLE

    def on_animation_end(self) -> None:
        super().on_animation_end()

        self.__animation_ended = True