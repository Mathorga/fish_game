import pyglet.math as pm

from amonite.animation import Animation

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

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.__startup = True
        self.__animation_ended = False

    def update(self, dt: float) -> str | None:
        # Handle animation end.
        if self.__animation_ended:
            if self.actor.move_vec.mag <= 0.0:
                return FishStates.IDLE
            else:
                return FishStates.SWIM

        if self.__startup:
            self.actor.move_vec = pm.Vec2.from_polar(self.actor.max_move_speed * 2, self.actor.move_vec.heading)
            self.__startup = False
        else:
            self.actor.move_vec = pm.Vec2.from_polar(self.actor.move_vec.mag - self.actor.move_accel / 2 * dt, self.actor.move_vec.heading)

        # Move the player.
        self.actor.move(dt = dt)

        # Check for state changes.
        if self.actor.move_vec.mag <= 0.0:
            return FishStates.IDLE

    def on_animation_end(self) -> None:
        self.__animation_ended = True