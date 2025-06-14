import pyglet
import pyglet.math as pm

from amonite.settings import SETTINGS
from amonite.settings import Keys
from amonite.animation import Animation
import amonite.controllers as controllers
from amonite.input_controller import ControllerStick

from constants import custom_setting_keys
from constants import uniques
from leg.leg_data_node import LegDataNode
from leg.states.leg_state import LegStates
from leg.states.leg_state import LegState

class LegJumpState(LegState):
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
        self.__animation: Animation = Animation(source = "sprites/leg/leg_jump.json")

        # Input.
        self.__move_vec: pyglet.math.Vec2 = pyglet.math.Vec2()

        # Other.
        self.__jump_force: float = 500.0
        self.__startup: bool = True

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.actor.grounded = False
        self.__jump_force = self.actor.jump_force * self.actor.get_jump_dampening()
        self.__startup = True

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move_vec: pm.Vec2 = controllers.INPUT_CONTROLLER.get_stick_vector(
                stick = ControllerStick.LSTICK,
                controller_index = uniques.LEG_CONTROLLER
            )

            # Only read keyboard input if so specified in settings.
            if SETTINGS[Keys.DEBUG] and SETTINGS[custom_setting_keys.KEYBOARD_CONTROLS]:
                self.__move_vec += controllers.INPUT_CONTROLLER.get_key_vector()

            self.__move_vec = self.__move_vec.normalize()

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        self.actor.compute_move_speed(dt = dt, move_vec = pm.Vec2(self.__move_vec.x, 0.0))
        self.actor.compute_gravity_speed(dt = dt)

        # Overwrite gravity speed on startup.
        if self.__startup:
            self.__startup = False
            self.actor.gravity_vec = pm.Vec2(0.0, self.__jump_force)

        # Move the player.
        self.actor.move(dt = dt)

        # Check for state changes.
        if self.actor.grounded:
            if self.actor.move_vec.length() <= 0.0:
                return LegStates.IDLE

            return LegStates.WALK

    def end(self) -> None:
        super().end()

        # Reset the actor jump force for the next jump.
        self.actor.jump_force = 0.0