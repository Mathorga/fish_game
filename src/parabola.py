import pyglet
import pyglet.math as pm
import math

from amonite.node import PositionNode
from amonite.sprite_node import SpriteNode

class Parabola(PositionNode):
    def __init__(
        self,
        sprite_resource: pyglet.image.Texture | pyglet.image.animation.Animation,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        speed: float = 10.0,
        angle: float = 45.0,
        gravity: float = 9.81,
        sections_count: int = 20,
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
        self.gravity: float = gravity
        self.sections_count: int = sections_count
        self.__batch: pyglet.graphics.Batch | None = batch

        self.__flight_time: float = 1.0
        self.__timestep: float = self.__flight_time / self.sections_count

        self.trajectory: list[pm.Vec2] = []
        self.steps: list[SpriteNode] = []
        for i in range(self.sections_count):
            self.trajectory.append(pm.Vec2())
            step_sprite: SpriteNode = SpriteNode(
                resource = sprite_resource,
                y_sort = False,
                batch = batch
            )
            self.steps.append(step_sprite)
            self.add_component(step_sprite)

        self.__compute_trajectory()

    def set_speed(self, speed: float) -> None:
        self.speed = speed

    def set_angle(self, angle: float) -> None:
        self.angle = angle
        self.__theta = math.radians(angle)

    def set_gravity(self, gravity: float) -> None:
        self.gravity = gravity

    def __compute_trajectory(self) -> None:
        for i in range(self.sections_count):
            t: float = self.__timestep * (i + 1)
            xt: float = self.x + self.speed * math.cos(self.__theta) * t
            yt: float = self.y + self.speed * math.sin(self.__theta) * t - 0.5 * self.gravity * t ** 2
            self.trajectory[i] = pm.Vec2(xt, yt)
            self.steps[i].set_position((xt, yt))
            t += self.__timestep

    def update(self, dt: float) -> None:
        super().update(dt)

        self.__compute_trajectory()