from typing import Any
from typing import Callable
import pyglet
import pyglet.math as pm
import pyglet.image as pimg

from amonite import controllers
from amonite.collision.collision_node import CollisionNode
from amonite.collision.collision_node import CollisionMethod
from amonite.collision.collision_node import CollisionType
from amonite.collision.collision_shape import CollisionRect
from amonite.node import PositionNode
from amonite.sprite_node import SpriteNode
from amonite.animation import Animation
from amonite.door_node import DOOR_COLOR

from constants import collision_tags
from constants import uniques
from interactable.interactable import Interactable

class DoorNode(PositionNode, Interactable):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        width: int = 0,
        height: int = 0,
        anchor_x: int = 0,
        anchor_y: int = 0,
        destination: str = "",
        on_triggered: Callable[[None], None] | None = None,
        batch: pyglet.graphics.Batch | None = None
    ) -> None:
        PositionNode.__init__(
            self,
            x = x,
            y = y,
            z = z
        )
        Interactable.__init__(
            self,
            one_shot = True
        )

        self.__door_closed_img: pimg.Animation = Animation(source = "sprites/door/door_closed.json").content
        self.__door_open_img: pimg.Animation = Animation(source = "sprites/door/door_open.json").content
        self.__door_opening_img: pimg.Animation = Animation(source = "sprites/door/door_opening.json").content

        self.__light_bulb_off_img: pimg.Animation = Animation(source = "sprites/lightbulbs/lightbulb_off.json").content
        self.__light_bulb_red_img: pimg.Animation = Animation(source = "sprites/lightbulbs/lightbulb_red.json").content
        self.__light_bulb_purple_img: pimg.Animation = Animation(source = "sprites/lightbulbs/lightbulb_purple.json").content

        self.__red_light_offset: pm.Vec2 = pm.Vec2(-8.0, 42.0)
        self.__purple_light_offset: pm.Vec2 = pm.Vec2(8.0, 42.0)

        self.__sprite: SpriteNode = SpriteNode(
            resource = self.__door_closed_img,
            y_sort = False,
            on_animation_end = self.__on_sprite_animation_end,
            batch = batch
        )
        self.__red_light_sprite: SpriteNode = SpriteNode(
            resource = self.__light_bulb_off_img,
            x = self.__red_light_offset.x,
            y = self.__red_light_offset.y,
            y_sort = False,
            batch = batch
        )
        self.__purple_light_sprite: SpriteNode = SpriteNode(
            resource = self.__light_bulb_off_img,
            x = self.__purple_light_offset.x,
            y = self.__purple_light_offset.y,
            y_sort = False,
            batch = batch
        )
        self.add_component(self.__sprite)
        self.add_component(self.__red_light_sprite)
        self.add_component(self.__purple_light_sprite)

        self.collider: CollisionNode = CollisionNode(
            collision_type = CollisionType.STATIC,
            collision_method = CollisionMethod.PASSIVE,
            passive_tags = [
                collision_tags.LEVEL_DOOR,
                collision_tags.INTERACTABLE
            ],
            sensor = True,
            on_triggered = self.__on_collision_triggered,
            color = DOOR_COLOR,
            shape = CollisionRect(
                width = width,
                height = height,
                anchor_x = anchor_x,
                anchor_y = anchor_y,
                batch = batch
            ),
            owner = self
        )

        self.add_component(self.collider)
        controllers.COLLISION_CONTROLLER.add_collider(self.collider)

        self.__on_triggered: Callable[[list[str], Any, bool], None] | None = on_triggered

        self.__fish_sensed: bool = False
        self.__leg_sensed: bool = False

        self.__open: bool = False
        self.__opening: bool = False

    def __on_sprite_animation_end(self) -> None:
        if self.__opening:
            self.__sprite.set_image(self.__door_open_img)
            self.__opening = False
            self.__open = True

    def __on_collision_triggered(self, tags: list[str], collider: CollisionNode, entered: bool) -> None:
        if collision_tags.FISH_SENSE in tags:
            self.__fish_sensed = entered

        if collision_tags.LEG_SENSE in tags:
            self.__leg_sensed = entered

    def update(self, dt: float) -> None:
        super().update(dt = dt)

        if self.__open or self.__opening:
            return

        # Turn on light for leg.
        purple_light_image: pyglet.image.AbstractImage | pyglet.image.animation.Animation = self.__purple_light_sprite.get_image()
        if self.__fish_sensed:
            if purple_light_image != self.__light_bulb_purple_img:
                self.__purple_light_sprite.set_image(self.__light_bulb_purple_img)
        else:
            if purple_light_image != self.__light_bulb_off_img:
                self.__purple_light_sprite.set_image(self.__light_bulb_off_img)

        # Turn on light for fish.
        red_light_image: pyglet.image.AbstractImage | pyglet.image.animation.Animation = self.__red_light_sprite.get_image()
        if self.__leg_sensed:
            if red_light_image != self.__light_bulb_red_img:
                self.__red_light_sprite.set_image(self.__light_bulb_red_img)
        else:
            if red_light_image != self.__light_bulb_off_img:
                self.__red_light_sprite.set_image(self.__light_bulb_off_img)

        # Open the door.
        if self.__leg_sensed and self.__fish_sensed:
            self.__sprite.set_image(self.__door_opening_img)
            self.__opening = True

    def delete(self):
        self.collider.delete()

        super().delete()

    def interact(
        self,
        tags: list[str]
    ):
        super().interact(tags = tags)

        if uniques.FISH_DOOR_TRIGGERED and collision_tags.FISH_SENSE in tags:
            uniques.FISH_DOOR_TRIGGERED = True
            uniques.FISH.toggle()

        if uniques.LEG_DOOR_TRIGGERED and collision_tags.LEG_SENSE in tags:
            uniques.LEG_DOOR_TRIGGERED = True
            uniques.LEG.toggle()