import pyglet

from amonite.node import PositionNode

from fish.water_fish.water_fish_node import WaterFishNode

class FishNode(PositionNode):
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

        self.__water_fish: WaterFishNode | None = WaterFishNode(
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