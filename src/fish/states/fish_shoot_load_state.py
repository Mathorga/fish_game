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
        self.__preload_animation: Animation = Animation(source = "sprites/fish/dumbo_shoot_preload.json")
        self.__load_animation: Animation = Animation(source = "sprites/fish/dumbo_shoot_load.json")
        ########################
        ########################

        ########################
        # Input.
        ########################
        self.__aim: bool = False
        self.__shoot: bool = False
        self.__aim_vec: pm.Vec2 = pm.Vec2()
        ########################
        ########################

        ########################
        # Other.
        ########################
        self.__preloading: bool = True

        # Time elapsed since state start, used to check for releasability.
        self.__elapsed: float = 0.0

        # Time (in seconds) before the player can release the shoot.
        self.__release_threshold: float = 1.0
        self.__animation_ended: bool = False

        self.__shoot_force: float = self.actor.min_shoot_force
        self.__shoot_force_step: float = 200.0

        # Threshold for showing ink.
        self.shoot_threshold: float = 0.1
        ########################
        ########################

    def start(self) -> None:
        self.__preloading = True
        self.__shoot_force = self.actor.min_shoot_force
        self.__aim = False
        self.__shoot = False
        self.__elapsed = 0.0
        self.__release_threshold = 1.0
        self.__animation_ended = False
        self.actor.set_animation(self.__preload_animation)
        self.actor.move_vec *= 0.0
        self.actor.set_shoot_force(self.__shoot_force)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__aim_vec = controllers.INPUT_CONTROLLER.get_stick_vector(
                stick = ControllerStick.LSTICK,
                controller_index = uniques.FISH_CONTROLLER
            )
            self.__aim = controllers.INPUT_CONTROLLER.get_button(
                button = ControllerButton.EAST,
                controller_index = uniques.FISH_CONTROLLER
            )
            self.__shoot = controllers.INPUT_CONTROLLER.get_button_release(
                button = ControllerButton.EAST,
                controller_index = uniques.FISH_CONTROLLER
            )

            # Only read keyboard input if so specified in settings.
            if SETTINGS[custom_setting_keys.KEYBOARD_CONTROLS]:
                self.__aim_vec += controllers.INPUT_CONTROLLER.get_key_vector()
                self.__aim = self.__aim or controllers.INPUT_CONTROLLER[pyglet.window.key.RSHIFT]
                self.__shoot = self.__shoot or controllers.INPUT_CONTROLLER.key_presses.get(pyglet.window.key.SPACE, False)

            self.__aim_vec = self.__aim_vec.normalize()
        else:
            self.__move_vec = pm.Vec2()
            self.__aim = False
            self.__shoot = False

    def __can_release(self) -> bool:
        return self.__animation_ended or self.__elapsed > self.__release_threshold

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        if self.__aim_vec.length() <= self.shoot_threshold:
            # Shoot threshold is not reached, so delete ink and reset shoot force.
            self.actor.delete_ink()
            self.__shoot_force = self.actor.min_shoot_force
        else:
            self.actor.spawn_ink()

            # Move the aiming around. This should also update the actor's facing.
            self.actor.aim_vec = self.__aim_vec
            self.actor.move_ink()

            self.__elapsed += dt
            self.__shoot_force += self.__shoot_force_step * dt

            # Make sure the shoot force does not exceed its maximum possible value.
            self.__shoot_force = pm.clamp(self.__shoot_force, 0.0, self.actor.max_shoot_force)

            self.actor.set_shoot_force(self.__shoot_force)

        self.actor.compute_move_speed(dt = dt, move_vec = pm.Vec2(0.0, 0.0))
        self.actor.compute_gravity_speed(dt = dt)

        self.actor.move(dt = dt)

        # Check for state changes.
        if self.actor.in_water:
            self.actor.delete_ink()
            return FishStates.SWIM

        if self.__shoot and self.__can_release:
            return FishStates.SHOOT

        if not self.__aim:
            # Make sure the ink is deleted if back to idle.
            self.actor.delete_ink()
            return FishStates.IDLE

    def on_animation_end(self) -> None:
        super().on_animation_end()

        if self.__preloading:
            self.__preloading = False
            self.actor.set_animation(self.__load_animation)
            return

        self.__animation_ended = True