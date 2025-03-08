from amonite.node import PositionNode

class MidCameraNode(PositionNode):
    """
    Positions itself between all given targets.
    """

    def __init__(
        self,
        targets: list[PositionNode],
        z: float = 0.0
    ) -> None:
        super().__init__(
            x = 0.0,
            y = 0.0,
            z = z
        )

        self.__targets: list[PositionNode] = targets

    def update(self, dt: float) -> None:
        super().update(dt = dt)

        total_x: float = 0.0
        total_y: float = 0.0

        for target in self.__targets:
            target_position: tuple[float, float] = target.get_position()
            total_x += target_position[0]
            total_y += target_position[1]

        total_x /= len(self.__targets)
        total_y /= len(self.__targets)

        self.set_position(position = (total_x, total_y))