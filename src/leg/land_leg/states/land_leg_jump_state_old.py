import pyglet
import pyglet.math as pm

from amonite.animation import Animation
import amonite.controllers as controllers

from leg.land_leg.land_leg_data_node import LandLegDataNode
from leg.land_leg.states.land_leg_state import LandLegStates
from leg.land_leg.states.land_leg_state import LandLegState

class LandLegJumpStateOld(LandLegState):
    def __init__(
        self,
        actor: LandLegDataNode
    ) -> None:
        super().__init__(actor = actor)

        # Animation.
        self.__animation: Animation = Animation(source = "sprites/leg/land_leg/land_leg_jump.json")
        self.__animation_ended: bool = False

        # Input.
        self.__move_vec: pyglet.math.Vec2 = pyglet.math.Vec2()

        # Other.
        self.__jump_force: float = 20.0
        self.__jump_vec: pm.Vec2 = pm.Vec2()

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.actor.grounded = False
        self.__animation_ended = False
        self.__jump_force = 20.0
        self.__jump_vec = pm.Vec2()

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move_vec = controllers.INPUT_CONTROLLER.get_movement_vec()

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        self.actor.compute_move_speed(dt = dt, move_vec = pm.Vec2(self.__move_vec.x, 0.0))
        self.actor.compute_gravity_speed(dt = dt)

        # if self.__startup:
        if self.__jump_vec.mag < 100.0:
            print(self.actor.gravity_vec)
            print(self.actor.move_vec)
            self.__jump_vec += pm.Vec2(0.0, self.__jump_force)
            self.actor.gravity_vec += self.__jump_vec

        # Move the player.
        self.actor.move(dt = dt)

        # Check for state changes.
        if self.actor.grounded:
            if self.actor.move_vec.mag <= 0.0:
                return LandLegStates.IDLE

            return LandLegStates.WALK

    def on_animation_end(self) -> None:
        self.__animation_ended = True