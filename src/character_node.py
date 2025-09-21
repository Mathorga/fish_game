import pyglet

from amonite.node import PositionNode

class CharacterNode(PositionNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        enabled: bool = True
    ) -> None:
        super().__init__(
            x = x,
            y = y,
            z = z
        )

        self.enabled: bool = enabled

    def toggle(self) -> None:
        self.enabled = not self.enabled

    def disable(self) -> None:
        self.enabled = False

    def enable(self) -> None:
        self.enabled = True