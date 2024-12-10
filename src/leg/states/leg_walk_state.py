from amonite.input_controller import ControllerButton, ControllerStick
import pyglet
import pyglet.math as pm

from amonite.animation import Animation
import amonite.controllers as controllers

import constants.collision_tags as collision_tags
from leg.leg_data_node import LegDataNode
from leg.states.leg_state import LegStates
from leg.states.leg_state import LegState

class LegWalkState(LegState):
    def __init__(
        self,
        actor: LegDataNode
    ) -> None:
        super().__init__(actor = actor)

        # Animation.
        self.__animation: Animation = Animation(source = "sprites/leg/leg_walk.json")

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
            self.__move_vec = (controllers.INPUT_CONTROLLER.get_stick_vector(ControllerStick.LSTICK) + controllers.INPUT_CONTROLLER.get_key_vector()).normalize()
            self.__jump = controllers.INPUT_CONTROLLER[pyglet.window.key.SPACE] or controllers.INPUT_CONTROLLER.get_button(ControllerButton.DOWN)

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        self.actor.compute_move_speed(dt = dt, move_vec = pm.Vec2(self.__move_vec.x, 0.0))
        self.actor.compute_gravity_speed(dt = dt)

        # Move the player.
        self.actor.move(dt = dt)

        # Check for state changes.
        if self.__jump and self.actor.grounded:
            return LegStates.JUMP_LOAD

        if self.actor.move_vec.mag <= 0.0:
            return LegStates.IDLE