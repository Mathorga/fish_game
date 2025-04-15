from amonite.animation import Animation

from fish.ink.ink_data_node import InkDataNode
from fish.ink.states.ink_state import InkState
from fish.ink.states.ink_state import InkStates

class InkFlyState(InkState):
    def __init__(
        self,
        actor: InkDataNode,
    ) -> None:
        super().__init__(
            actor = actor,
        )

        self.__animation: Animation = Animation(source = "sprites/fish/ink_fly.json")

        self.__collided: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.__collided = False

    def update(self, dt: float) -> str | None:
        self.actor.compute_move_speed(dt = dt, move_vec = self.actor.shoot_vec)
        self.actor.compute_gravity_speed(dt = dt)

        self.actor.move(dt = dt)

        # Check for state changes.
        if self.__collided:
            return InkStates.SPLAT
        
    def on_collision(self, tags: list[str], enter: bool) -> None:
        # TODO Check for the right collision tags.
        self.__collided = True