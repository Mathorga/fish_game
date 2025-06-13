import pyglet
import pyglet.math as pm

from amonite.animation import Animation
import amonite.controllers as controllers
from amonite.input_controller import ControllerStick

from constants import uniques
from fish.fish_data_node import FishDataNode
from fish.states.fish_state import FishStates
from fish.states.fish_state import FishState

class FishIdleState(FishState):
    def __init__(
        self,
        actor: FishDataNode,
        input_enabled: bool = True
    ) -> None:
        super().__init__(
            actor = actor,
            input_enabled = input_enabled
        )

        self.__land_animation: Animation = Animation(source = "sprites/fish/dumbo_land_idle.json")
        self.__midair_animation: Animation = Animation(source = "sprites/fish/dumbo_swim.json")
        self.__animation: Animation = self.__land_animation if self.actor.grounded else self.__midair_animation

        # Inputs.
        self.__move: bool = False
        self.__aim_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__interact: bool = False

    def __update_animation(self) -> None:
        if self.actor.grounded and self.__animation != self.__land_animation:
            self.__animation = self.__land_animation
            self.actor.set_animation(self.__animation)
            return

        if not self.actor.grounded and self.__animation != self.__midair_animation:
            self.__animation = self.__midair_animation
            self.actor.set_animation(self.__animation)
            return

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.__update_animation()
        self.actor.aim_vec *= 0.0

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move = controllers.INPUT_CONTROLLER.get_movement(
                controller_index = uniques.FISH_CONTROLLER
            )
            self.__aim_vec = (
                controllers.INPUT_CONTROLLER.get_stick_vector(
                    stick = ControllerStick.RSTICK,
                    controller_index = uniques.FISH_CONTROLLER
                ) +
                controllers.INPUT_CONTROLLER.get_key_vector(
                    up = pyglet.window.key.I,
                    left = pyglet.window.key.J,
                    down = pyglet.window.key.K,
                    right = pyglet.window.key.L
                )
            ).normalize()
            self.__interact = controllers.INPUT_CONTROLLER.key_presses.get(pyglet.window.key.H, False)

    def update(self, dt: float) -> str | None:
        self.__update_animation()

        # Read inputs.
        self.__fetch_input()

        if self.__interact:
            self.actor.interact()

        self.actor.compute_move_speed(dt = dt, move_vec = pm.Vec2(0.0, 0.0))
        self.actor.compute_gravity_speed(dt = dt)

        self.actor.move(dt = dt)

        # Check for state changes.
        if self.actor.in_water:
            return FishStates.SWIM

        if self.__aim_vec.length() > 0.0:
            self.actor.aim_vec = self.__aim_vec
            return FishStates.SHOOT_LOAD

        if self.__move:
            return FishStates.CRAWL