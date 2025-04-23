from amonite.animation import Animation

from fish.ink.ink_data_node import InkDataNode
from fish.ink.states.ink_state import InkState

class InkSplatState(InkState):
    def __init__(
        self,
        actor: InkDataNode,
    ) -> None:
        super().__init__(
            actor = actor,
        )

        self.__animation: Animation = Animation(source = "sprites/fish/ink_splat.json")

        self.__animation_ended: bool = False

    def start(self) -> None:
        super().start()

        self.__animation_ended = False

        self.actor.set_animation(self.__animation)

    def update(self, dt: float) -> str | None:
        super().update(dt)

        # Delete upon animation end.
        if self.__animation_ended:
            self.actor.trigger_delete()

        self.actor.move(dt = dt)

    def on_animation_end(self) -> None:
        super().on_animation_end()

        self.__animation_ended = True