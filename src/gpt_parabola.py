import pyglet
import pyglet.math as pm
import math

from amonite.node import PositionNode
from amonite.shapes.circle_node import CircleNode

class GPTParabola(PositionNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        speed: float = 10.0,
        angle: float = 45.0,
        timestep: float = 0.1,
        gravity: float = 9.81,
        batch: pyglet.graphics.Batch | None = None
    ) -> None:
        super().__init__(
            x = x,
            y = y,
            z = z
        )

        self.speed: float = speed
        self.angle: float = angle
        self.__theta: float = math.radians(angle)
        self.timestep: float = timestep
        self.gravity: float = gravity
        self.__flight_time: float = (2 * speed * math.sin(self.__theta)) / gravity

        self.trajectory: list[pm.Vec2] = []
        self.steps: list[PositionNode] = []
        for i in range(int(self.__flight_time / timestep) + 1):
            self.trajectory.append(pm.Vec2())
            step: PositionNode = CircleNode(
                x = 0.0,
                y = 0.0,
                radius = 2,
                batch = batch
            )
            self.steps.append(step)
            self.add_component(step)

        self.__compute_trajectory()

    def set_speed(self, speed: float) -> None:
        self.speed = speed

    def set_angle(self, angle: float) -> None:
        self.angle = angle
        self.__theta = math.radians(angle)

    def set_gravity(self, gravity: float) -> None:
        self.gravity = gravity

    def __compute_trajectory(self) -> None:
        t: float = 0.0
        i: int = 0

        while t <= self.__flight_time:
            xt: float = self.x + self.speed * math.cos(self.__theta) * t
            yt: float = self.y + self.speed * math.sin(self.__theta) * t - 0.5 * self.gravity * t ** 2
            self.trajectory[i] = pm.Vec2(xt, yt)
            self.steps[i].set_position((xt, yt))
            t += self.timestep
            i += 1

    def update(self, dt: float) -> None:
        super().update(dt)

        self.__compute_trajectory()

# parabola: GCPParabola = GCPParabola(
#     x = 100.0,
#     y = 100.0,
#     speed = 100.0,
#     angle = 70.0
# )

# # Pyglet window
# window = pyglet.window.Window(800, 600)
# batch = pyglet.graphics.Batch()

# @window.event
# def on_draw():
#     window.clear()
#     for x, y in parabola.trajectory:
#         pyglet.shapes.Circle(x, y, 2, color=(255, 0, 0), batch=batch).draw()
#     batch.draw()

# pyglet.app.run()