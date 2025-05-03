import pyglet

from amonite.node import PositionNode

class ButtonNode(PositionNode):
    def __init__(
        self,
        x = 0.0,
        y = 0.0,
        z = 0.0,
        batch: pyglet.graphics.Batch | None = None
    ):
        super().__init__(
            x = x,
            y = y,
            z = z
        )

        self.__batch: pyglet.graphics.Batch | None = batch