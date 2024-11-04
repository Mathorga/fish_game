import pyglet

from amonite.node import PositionNode

from leg.land_leg.land_leg_node import LandLegNode

class LegNode(PositionNode):
    __slots__ = (
        "__water_fish"
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

        self.__water_fish: LandLegNode | None = LandLegNode(
            x = x,
            y = y,
            z = z,
            batch = batch
        )

    def update(self, dt: float) -> None:
        super().update(dt)

        if self.__water_fish is not None:
            self.__water_fish.update(dt = dt)

    def delete(self) -> None:
        # Delete water fish node.
        if self.__water_fish is not None:
            self.__water_fish.delete()
            self.__water_fish = None

        super().delete()