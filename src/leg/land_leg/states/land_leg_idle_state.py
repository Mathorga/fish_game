import pyglet.math as pm

from amonite.animation import Animation
import amonite.controllers as controllers

from leg.land_leg.land_leg_data_node import LandLegDataNode
from leg.land_leg.states.land_leg_state import LandLegStates
from leg.land_leg.states.land_leg_state import LandLegState

class LandLegIdleState(LandLegState):
    def __init__(
        self,
        actor: LandLegDataNode
    ) -> None:
        super().__init__(actor = actor)

        self.__animation: Animation = Animation(source = "sprites/leg/land_leg/land_leg_idle.json")

        # Inputs.
        self.__move: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move = controllers.INPUT_CONTROLLER.get_movement()

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        # Apply gravity to actor speed and move it.
        self.actor.speed
        self.actor.move_dir
        actor_velocity: pm.Vec2 = pm.Vec2.from_polar(
            mag = self.actor.speed,
            angle = self.actor.move_dir
        )

        actor_velocity.y -= 0.5

        self.actor.speed = actor_velocity.mag
        self.actor.move_dir = actor_velocity.heading

        self.actor.move(dt = dt)

        # Check for state changes.
        if self.__move:
            return LandLegStates.WALK