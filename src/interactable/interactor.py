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
from interactable.interactable import Interactable

class Interactor(PositionNode):
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
        self.__interactables: list[Interactable] = []
        self.__button_offset: pm.Vec2 = pm.Vec2(0.0, 32.0)

        self.__button_signal: SpriteNode | None = None

        self.__interact_sensor: CollisionNode = CollisionNode(
            collision_type = CollisionType.DYNAMIC,
            collision_method = CollisionMethod.PASSIVE,
            sensor = True,
            active_tags = [
                collision_tags.INTERACTABLE
            ],
            passive_tags = [],
            shape = sensor_shape if sensor_shape is not None else CollisionRect(
                anchor_x = 5,
                anchor_y = 5,
                width = 10,
                height = 10,
                batch = batch
            ),
            on_triggered = self.on_interactable_found
        )
        self.add_component(self.__interact_sensor)
        controllers.COLLISION_CONTROLLER.add_collider(self.__interact_sensor)


    def update(self, dt: float) -> None:
        super().update(dt = dt)

        position: tuple[float, float] = self.get_position()

        if self.__button_signal is not None:
            self.__button_signal.set_position(
                position = (
                    position[0] + self.__button_offset.x,
                    position[1] + self.__button_offset.y
                )
            )

        self.toggle_button_signal()

    def on_interactable_found(self, tags: list[str], collider: CollisionNode, entered: bool) -> None:
        if collider.owner is not None and isinstance(collider.owner, Interactable) and collider.owner.is_active():
            if entered and self.__button_signal is None:
                self.__interactables.append(collider.owner)
            elif not entered:
                self.__interactables.remove(collider.owner)

    def toggle_button_signal(self) -> None:
        if len(self.__interactables) > 0 and self.__button_signal is None:
            self.__button_signal = self.__build_button_signal()
            self.add_component(self.__button_signal)
        elif len(self.__interactables) <= 0 and self.__button_signal is not None:
            # TODO Amonite's PositionNode should expose a "remove_component" mehtod.
            self.components.remove(self.__button_signal)
            self.__button_signal.delete()
            self.__button_signal = None

    def interact(
        self,
        tags: list[str]
    ) -> None:
        """
        Triggers interaction with the first interactable perceived.
        All tags are passed through to the interactable.
        """

        # Only interact with the first interactable in line.
        if len(self.__interactables) > 0:
            interactable: Interactable = self.__interactables[0]
            interactable.interact(tags = tags)

            if not interactable.is_active():
                self.__interactables.remove(interactable)

    def __build_button_signal(self) -> SpriteNode:
        position: tuple[float, float] = self.get_position()
        return SpriteNode(
            resource = Animation(source = "sprites/button_icon/button_icon.json").content,
            x = position[0] + self.__button_offset.x,
            y = position[1] + self.__button_offset.y,
            y_sort = False,
            batch = self.__batch
        )