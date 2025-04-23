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

        self.__animation: Animation = Animation(source = "sprites/fish/ink_fly.json")

    def start(self) -> None:
        self.actor.set_animation(self.__animation)