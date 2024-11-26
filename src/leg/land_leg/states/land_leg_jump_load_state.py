import pyglet
import pyglet.math as pm

from amonite.animation import Animation
import amonite.controllers as controllers

from leg.land_leg.land_leg_data_node import LandLegDataNode
from leg.land_leg.states.land_leg_state import LandLegStates
from leg.land_leg.states.land_leg_state import LandLegState

class LandLegJumpLoadState(LandLegState):
    def __init__(
        self,
        actor: LandLegDataNode
    ) -> None:
        super().__init__(actor = actor)

        # Animation.
        self.__animation: Animation = Animation(source = "sprites/leg/land_leg/land_leg_jump_load.json")

        # Input.
        self.__jump: bool = False

        # Other.
        self.__elapsed: float = 0.0
        self.__release_threshold: float = 1.0
        self.__animation_ended: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.__jump = False
        self.__elapsed = 0.0
        self.__release_threshold = 1.0
        self.__animation_ended = False

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__jump = controllers.INPUT_CONTROLLER[pyglet.window.key.SPACE] or controllers.INPUT_CONTROLLER.buttons.get("b", False)

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        self.__elapsed += dt

        # Check for state changes.
        if not self.__jump:
            if self.can_release():
                return LandLegStates.JUMP

            return LandLegStates.IDLE

    def can_release(self) -> bool:
        return self.__animation_ended or self.__elapsed > self.__release_threshold

    def on_animation_end(self) -> None:
        super().on_animation_end()

        self.__animation_ended = True