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
        self.__grabbables: list[Grabbable] = []
        self.__grabbed: Grabbable | None = None
        self.__on: bool = True
        self.__button_offset: pm.Vec2 = pm.Vec2(0.0, 32.0)
        self.__grabbable_offset: pm.Vec2 = pm.Vec2(0.0, 26.0)

        self.__button_signal: SpriteNode | None = None

        self.__grab_sensor: CollisionNode = CollisionNode(
            collision_type = CollisionType.DYNAMIC,
            collision_method = CollisionMethod.PASSIVE,
            sensor = True,
            active_tags = [
                collision_tags.GRABBABLE
            ],
            passive_tags = [],
            shape = sensor_shape if sensor_shape is not None else CollisionRect(
                anchor_x = 5,
                anchor_y = 5,
                width = 10,
                height = 10,
                batch = batch
            ),
            on_triggered = self.on_grabbable_found
        )
        self.add_component(self.__grab_sensor)
        controllers.COLLISION_CONTROLLER.add_collider(self.__grab_sensor)


    def update(self, dt: float) -> None:
        super().update(dt = dt)

        position: tuple[float, float] = self.get_position()

        # Update grabbables position.
        if self.__grabbed is not None:
            self.__grabbed.move_to((position[0] + self.__grabbable_offset.x, position[1] + self.__grabbable_offset.y))

        self.toggle_grabbable_button()

    def __turn_button_signal_on(self) -> None:
        if self.__button_signal is None:
            self.__button_signal = self.__build_button_signal()
            self.add_component(self.__button_signal)

    def __turn_button_signal_off(self) -> None:
        if self.__button_signal is not None:
            if uniques.ACTIVE_SCENE is not None:
                uniques.ACTIVE_SCENE.remove_child(self.__button_signal)
            # TODO Amonite's PositionNode should expose a "remove_component" mehtod.
            self.components.remove(self.__button_signal)
            self.__button_signal.delete()
            self.__button_signal = None

    def on_grabbable_found(self, tags: list[str], collider: CollisionNode, entered: bool) -> None:
        if collider.owner is None:
            return

        if not isinstance(collider.owner, Grabbable):
            return

        if entered:
            self.__grabbables.append(collider.owner)
        elif collider.owner in self.__grabbables:
            self.__grabbables.remove(collider.owner)

    def toggle_grabbable_button(self) -> None:
        if self.__on and len(self.__grabbables) > 0 and self.__grabbed is None:
            self.__turn_button_signal_on()
        elif (len(self.__grabbables) <= 0 or self.__grabbed is not None):
            self.__turn_button_signal_off()

    def grab(self) -> None:
        if not self.__on:
            return

        if len(self.__grabbables) <= 0:
            return

        self.__grabbed = self.__grabbables[0]

        if not isinstance(self.__grabbed, Grabbable):
            return

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

    def turn_on(self) -> None:
        self.__on = True

    def turn_off(self) -> None:
        self.__on = False
        self.__turn_button_signal_off()

    def is_grabbing(self) -> bool:
        return self.__grabbed is not None

    def __build_button_signal(self) -> SpriteNode:
        return SpriteNode(
            resource = Animation(source = "sprites/button_icon/button_icon.json").content,
            x = self.__button_offset.x,
            y = self.__button_offset.y,
            y_sort = False,
            batch = self.__batch
        )