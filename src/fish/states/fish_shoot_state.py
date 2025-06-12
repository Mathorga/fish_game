from amonite.animation import Animation

from fish.fish_data_node import FishDataNode
from fish.states.fish_state import FishStates
from fish.states.fish_state import FishState

class FishShootState(FishState):
    def __init__(
        self,
        actor: FishDataNode,
        input_enabled: bool = True
    ) -> None:
        super().__init__(
            actor = actor,
            input_enabled = input_enabled
        )

        self.__animation: Animation = Animation(source = "sprites/fish/dumbo_idle.json")

        # Other.
        self.__animation_ended: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.actor.shoot_ink()
        self.__animation_ended = False

    def update(self, dt: float) -> str | None:
        # Handle animation end.
        if self.__animation_ended:
            return FishStates.IDLE

        self.actor.compute_gravity_speed(dt = dt)

        self.actor.move(dt = dt)

        # Check for state changes.
        if self.actor.in_water:
            return FishStates.SWIM

    def end(self) -> None:
        super().end()

        self.actor.aim_vec *= 0.0

    def on_animation_end(self) -> None:
        super().on_animation_end()

        self.__animation_ended = True