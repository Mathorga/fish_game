import pyglet
import pyglet.math as pm

from amonite.animation import Animation
from amonite import controllers

from fish.fish_data_node import FishDataNode
from fish.states.fish_state import FishStates
from fish.states.fish_state import FishState

class FishDashState(FishState):
    def __init__(
        self,
        actor: FishDataNode
    ) -> None:
        super().__init__(actor = actor)

        # Animation.
        self.__animation: Animation = Animation(source = "sprites/fish/dumbo_swim_dash.json")
        self.__startup: bool = False
        self.__animation_ended: bool = False

        # Input.
        self.__move_vec: pyglet.math.Vec2 = pyglet.math.Vec2()

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.__startup = True
        self.__animation_ended = False

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move_vec = controllers.INPUT_CONTROLLER.get_movement_vec(controller_index = 1)

    def update(self, dt: float) -> str | None:
        # Handle animation end.
        if self.__animation_ended:
            if self.actor.move_vec.length() <= 0.0:
                return FishStates.IDLE
            else:
                return FishStates.SWIM

        # Fetch inputs.
        self.__fetch_input()

        if self.__startup:
            self.actor.move_vec += pm.Vec2.from_polar(
                length = self.actor.max_move_speed * 5,
                angle = self.actor.move_vec.heading()
            )
            self.__startup = False

        self.actor.compute_move_speed(dt = dt, move_vec = self.__move_vec, max_speed = self.actor.dash_force)
        self.actor.compute_gravity_speed(dt = dt)

        # Move the player.
        self.actor.move(dt = dt)

        # Check for state changes.
        # Make sure the state ends when there's no more movement.
        # TODO Maybe animation end is enough for state change, since keeping the animation going
        # on movement exhaustion is probably better UX than cutting the animation abruptly.
        if self.actor.move_vec.length() <= 0.0:
            return FishStates.IDLE

    def on_animation_end(self) -> None:
        self.__animation_ended = True