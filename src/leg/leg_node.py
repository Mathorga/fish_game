import pyglet

from amonite.node import PositionNode

from leg.land_leg.land_leg_node import LandLegNode

class LegNode(PositionNode):
    __slots__ = (
        "__land_leg"
    )

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        batch: pyglet.graphics.Batch | None = None
    ) -> None:
        super().__init__(
            x = x,
            y = y,
            z = z
        )

        self.__land_leg: LandLegNode | None = LandLegNode(
            x = x,
            y = y,
            z = z,
            batch = batch
        )

    def update(self, dt: float) -> None:
        super().update(dt)

        if self.__land_leg is not None:
            self.__land_leg.update(dt = dt)

    def delete(self) -> None:
        # Delete water fish node.
        if self.__land_leg is not None:
            self.__land_leg.delete()
            self.__land_leg = None

        super().delete()