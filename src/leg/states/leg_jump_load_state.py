import pyglet
import pyglet.math as pm

from amonite.settings import SETTINGS
from amonite.settings import Keys
from amonite.animation import Animation
from amonite import controllers
from amonite.input_controller import ControllerButton
from amonite.input_controller import ControllerStick

from constants import custom_setting_keys
from constants import uniques
from leg.leg_data_node import LegDataNode
from leg.states.leg_state import LegStates
from leg.states.leg_state import LegState

class LegJumpLoadState(LegState):
    def __init__(
        self,
        actor: LegDataNode,
        input_enabled: bool = True
    ) -> None:
        super().__init__(
            actor = actor,
            input_enabled = input_enabled
        )

        ########################
        # Animation.
        ########################
        self.__animation: Animation = Animation(source = "sprites/leg/leg_jump_load.json")
        ########################
        ########################

        ########################
        # Input.
        ########################
        self.__jump: bool = False
        self.__move_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        ########################
        ########################

        ########################
        # Other.
        ########################
        # Time elapsed since state start, used to check for releasability.
        self.__elapsed: float = 0.0

        # Time (in seconds) before the player can release the jump.
        self.__release_threshold: float = 1.0
        self.__animation_ended: bool = False

        self.__jump_force_step: float = 500.0
        ########################
        ########################

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.actor.jump_force = 0.0
        self.__jump = False
        self.__elapsed = 0.0
        self.__release_threshold = 1.0
        self.__animation_ended = False

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move_vec: pm.Vec2 = controllers.INPUT_CONTROLLER.get_stick_vector(
                stick = ControllerStick.LSTICK,
                controller_index = uniques.LEG_CONTROLLER
            )
            self.__jump = controllers.INPUT_CONTROLLER.get_button(
                button = ControllerButton.SOUTH,
                controller_index = uniques.LEG_CONTROLLER
            )

            # Only read keyboard input if so specified in settings.
            if SETTINGS[Keys.DEBUG] and SETTINGS[custom_setting_keys.KEYBOARD_CONTROLS]:
                self.__move_vec += controllers.INPUT_CONTROLLER.get_key_vector()
                self.__jump += controllers.INPUT_CONTROLLER[pyglet.window.key.SPACE]

            self.__move_vec = self.__move_vec.normalize()

    def __can_release(self) -> bool:
        return self.__animation_ended or self.__elapsed > self.__release_threshold

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        # Applying move speed accounts for updating the actor's facing direction.
        self.actor.compute_move_speed(dt = dt, move_vec = pm.Vec2(self.__move_vec.x, 0.0))

        self.__elapsed += dt
        self.actor.jump_force += self.__jump_force_step * dt

        # Make sure the jump force does not exceed its maximum possible value.
        self.actor.jump_force = pm.clamp(self.actor.jump_force, 0.0, self.actor.get_max_jump_force())

        # Check for state changes.
        if not self.__jump:
            if self.__can_release():
                return LegStates.JUMP

            return LegStates.IDLE

    def on_animation_end(self) -> None:
        super().on_animation_end()

        self.__animation_ended = True