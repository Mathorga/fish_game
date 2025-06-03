import pyglet
import pyglet.math as pm

from amonite.animation import Animation
from amonite import controllers
from amonite.input_controller import ControllerButton
from amonite.input_controller import ControllerStick

from constants import uniques
from fish.fish_data_node import FishDataNode
from fish.states.fish_state import FishState, FishStates

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
        self.__animation: Animation = Animation(source = "sprites/fish/dumbo_swim_dash.json")
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

        self.__shoot_force_step: float = 500.0
        ########################
        ########################

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.actor.shoot_force = 0.0
        self.__shoot = False
        self.__elapsed = 0.0
        self.__release_threshold = 1.0
        self.__animation_ended = False
        self.actor.spawn_ink()

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__shoot = controllers.INPUT_CONTROLLER.key_presses.get(
                pyglet.window.key.SPACE,
                False
            ) or controllers.INPUT_CONTROLLER.get_button_presses(
                button = ControllerButton.DOWN,
                controller_index = uniques.FISH_CONTROLLER
            )
            self.__aim_vec = (
                controllers.INPUT_CONTROLLER.get_stick_vector(
                    stick = ControllerStick.RSTICK,
                    controller_index = uniques.FISH_CONTROLLER
                ) + controllers.INPUT_CONTROLLER.get_key_vector(
                    up = pyglet.window.key.I,
                    left = pyglet.window.key.J,
                    down = pyglet.window.key.K,
                    right = pyglet.window.key.L
                )
            ).normalize()

    def __can_release(self) -> bool:
        return self.__animation_ended or self.__elapsed > self.__release_threshold

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        # Move the aiming around. This should also update the actor's facing.
        self.actor.aim_vec = self.__aim_vec
        self.actor.move_ink()

        self.__elapsed += dt
        self.actor.shoot_force += self.__shoot_force_step * dt

        # Make sure the shoot force does not exceed its maximum possible value.
        self.actor.shoot_force = pm.clamp(self.actor.shoot_force, 0.0, self.actor.max_shoot_force)

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