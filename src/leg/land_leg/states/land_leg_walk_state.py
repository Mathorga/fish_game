import pyglet
import pyglet.math as pm

from amonite.animation import Animation
import amonite.controllers as controllers

from leg.land_leg.land_leg_data_node import LandLegDataNode
from leg.land_leg.states.land_leg_state import LandLegStates
from leg.land_leg.states.land_leg_state import LandLegState

class LandLegWalkState(LandLegState):
    def __init__(
        self,
        actor: LandLegDataNode
    ) -> None:
        super().__init__(actor = actor)

        # Animation.
        self.__animation: Animation = Animation(source = "sprites/leg/land_leg/land_leg_walk.json")

        # Input.
        self.__move_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__jump: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move_vec = controllers.INPUT_CONTROLLER.get_movement_vec()
            self.__jump = controllers.INPUT_CONTROLLER.get_sprint()

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        self.actor.compute_move_speed(dt = dt, move_vec = pm.Vec2(self.__move_vec.x, 0.0))
        self.actor.compute_gravity_speed(dt = dt)

        # Move the player.
        self.actor.move(dt = dt)

        # Check for state changes.
        if self.__jump and self.actor.grounded:
            return LandLegStates.JUMP_LOAD

        if self.actor.move_vec.mag <= 0.0:
            return LandLegStates.IDLE