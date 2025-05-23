import pyglet
import pyglet.math as pm

import amonite.controllers as controllers
from amonite.node import PositionNode
from amonite.sprite_node import SpriteNode
from amonite.animation import Animation
from amonite.collision.collision_node import CollisionNode
from amonite.collision.collision_node import CollisionType
from amonite.collision.collision_shape import CollisionShape
from amonite.collision.collision_shape import CollisionRect
from amonite.collision.collision_node import CollisionMethod

from constants import collision_tags
from constants import uniques
from grabbable.grabbable import Grabbable

class Grabber(PositionNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        sensor_shape: CollisionShape | None = None,
        batch: pyglet.graphics.Batch | None = None
    ):
        super().__init__(
            x = x,
            y = y
        )

        self.__batch: pyglet.graphics.Batch | None = batch
        self.__grabbables: list[PositionNode] = []
        self.__grabbed: PositionNode | None = None
        self.__button_offset: pm.Vec2 = pm.Vec2(0.0, 32.0)
        self.__grabbable_offset: pm.Vec2 = pm.Vec2(0.0, 26.0)

        self.__grab_button: SpriteNode | None = None

        self.__grab_sensor: CollisionNode = CollisionNode(
            x = x,
            y = y,
            collision_type = CollisionType.DYNAMIC,
            collision_method = CollisionMethod.PASSIVE,
            sensor = True,
            active_tags = [
                collision_tags.GRABBABLE
            ],
            passive_tags = [],
            shape = sensor_shape if sensor_shape is not None else CollisionRect(
                x = x,
                y = y,
                anchor_x = 5,
                anchor_y = 5,
                width = 10,
                height = 10,
                batch = batch
            ),
            on_triggered = self.on_grabbable_found
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.__grab_sensor)


    def update(self, dt: float) -> None:
        super().update(dt = dt)

        position: tuple[float, float] = self.get_position()

        if self.__grab_button is not None:
            self.__grab_button.set_position(
                position = (
                    position[0] + self.__button_offset.x,
                    position[1] + self.__button_offset.y
                )
            )

        # Update grabbables position.
        if self.__grabbed is not None:
            self.__grabbed.set_position(position + self.__grabbable_offset)

        self.__grab_sensor.set_position(position)

        self.toggle_grabbable_button()

    def delete(self):
        self.__grab_sensor.delete()
        if self.__grab_button is not None:
            self.__grab_button.delete()
        super().delete()

    def on_grabbable_found(self, tags: list[str], collider: CollisionNode, entered: bool) -> None:
        if entered and self.__grab_button is None and self.__grabbed is None:
            self.__grabbables.append(collider.owner)
        elif not entered and self.__grab_button is not None:
            self.__grabbables.remove(collider.owner)

    def toggle_grabbable_button(self) -> None:
        if len(self.__grabbables) > 0 and self.__grabbed is None and self.__grab_button is None:
            self.__grab_button = self.__build_grab_button()
            uniques.ACTIVE_SCENE.add_child(self.__grab_button)
        elif (len(self.__grabbables) <= 0 or self.__grabbed is not None) and self.__grab_button is not None:
            uniques.ACTIVE_SCENE.remove_child(self.__grab_button)
            self.__grab_button.delete()
            self.__grab_button = None

    def grab(self) -> None:
        if len(self.__grabbables) > 0:
            self.__grabbed = self.__grabbables[0]
            if isinstance(self.__grabbed, Grabbable):
                self.__grabbed.toggle_grab(True)

    def drop(self) -> None:
        if self.__grabbed is not None:
            if isinstance(self.__grabbed, Grabbable):
                self.__grabbed.toggle_grab(False)
            self.__grabbed = None

    def toggle_grab(self) -> None:
        if self.__grabbed is None:
            self.grab()
        else:
            self.drop()

    def __build_grab_button(self) -> SpriteNode:
        position: tuple[float, float] = self.get_position()
        return SpriteNode(
            resource = Animation(source = "sprites/button_icon/button_icon.json").content,
            x = position[0] + self.__button_offset.x,
            y = position[1] + self.__button_offset.y,
            y_sort = False,
            batch = self.__batch
        )