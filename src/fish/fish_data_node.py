import math
import time
from typing import Callable
import pyglet
import pyglet.math as pm

import amonite.controllers as controllers
from amonite.node import PositionNode
from amonite.sprite_node import SpriteNode
from amonite.animation import Animation
from amonite.collision.collision_node import CollisionNode
from amonite.collision.collision_node import CollisionType
from amonite.collision.collision_shape import CollisionRect
from amonite.collision.collision_node import CollisionMethod
from amonite.settings import SETTINGS
from amonite.settings import GLOBALS
from amonite.settings import Keys

from constants import collision_tags
from constants import uniques
from interactable.interactor import Interactor
from grabbable.grabbable import Grabbable
from fish.ink.ink_node import InkNode


class FishDataNode(PositionNode, Grabbable):
    """
    """

    # __slots__ = (
    #     "__batch",
    #     "speed",
    #     "max_speed",
    #     "accel",
    #     "__move_dir",
    #     "__hor_facing",
    #     "sprite",
    #     "__collider"
    # )

    water_move_dampening: float = 1.0
    land_move_dampening: float = 0.5

    water_gravity_dampening: float = 0.2
    land_gravity_dampening: float = 0.5

    max_shoot_force: float = 1600.0

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        on_sprite_animation_end: Callable | None = None,
        batch: pyglet.graphics.Batch | None = None
    ) -> None:
        PositionNode.__init__(self, x, y, z)
        Grabbable.__init__(self)

        self.__batch: pyglet.graphics.Batch | None = batch
        self.__hor_facing: int = 1
        self.heading: float = 0.0
        self.ink: InkNode | None = None
        self.__interactor: Interactor = Interactor(
            sensor_shape = CollisionRect(
                anchor_x = 15,
                anchor_y = 20,
                width = 30,
                height = 30,
                batch = batch
            ),
            batch = batch
        )
        self.add_component(self.__interactor)


        ################################
        # Input movement.
        ################################
        self.move_vec: pm.Vec2 = pm.Vec2(0.0, 0.0)
        self.max_move_speed: float = 80.0
        self.move_accel: float = 400.0
        ################################
        ################################


        ################################
        # Gravity movement.
        ################################
        self.gravity_vec: pm.Vec2 = pm.Vec2(0.0, 0.0)
        self.target_gravity_speed: float = math.inf
        self.gravity_accel: pm.Vec2 = pm.Vec2(0.0, -800.0)
        ################################
        ################################


        ################################
        # Collision flags.
        ################################
        self.__ground_collision_ids: set[int] = set()
        self.grounded: bool = False
        self.in_water: bool = False
        self.__interactables: set[PositionNode] = set()
        ################################
        ################################


        self.dash_force: float = self.max_move_speed * 3
        self.shoot_force: float = self.max_shoot_force
        self.aim_vec: pm.Vec2 = pm.Vec2(0.0, 0.0)
        self.ink_offset: pm.Vec2 = pm.Vec2(16.0, 16.0)


        ################################
        # Sprite
        ################################
        self.sprite: SpriteNode = SpriteNode(
            resource = Animation(source = "sprites/fish/dumbo_swim.json").content,
            y_sort = False,
            on_animation_end = on_sprite_animation_end,
            batch = batch
        )
        self.add_component(self.sprite)
        ################################
        ################################


        ################################
        # Colliders
        ################################
        self.__collider: CollisionNode = CollisionNode(
            # This collider drives the whole body position, so set its position to be the one provided.
            x = x,
            y = y,
            collision_type = CollisionType.DYNAMIC,
            active_tags = [
                collision_tags.PLAYER_COLLISION,
                collision_tags.PLAYER_SENSE,
                collision_tags.FALL,
                collision_tags.WATER
            ],
            passive_tags = [],
            shape = CollisionRect(
                anchor_x = 5,
                anchor_y = 7,
                width = 10,
                height = 14,
                batch = batch
            ),
            on_triggered = self.on_collision
        )
        self.__ground_sensor: CollisionNode = CollisionNode(
            collision_type = CollisionType.DYNAMIC,
            collision_method = CollisionMethod.PASSIVE,
            sensor = True,
            active_tags = [
                collision_tags.PLAYER_COLLISION
            ],
            passive_tags = [],
            shape = CollisionRect(
                anchor_x = 5,
                anchor_y = 8,
                width = 10,
                height = 2,
                batch = batch
            ),
            on_triggered = self.on_ground_collision
        )
        self.__grab_trigger: CollisionNode = CollisionNode(
            collision_type = CollisionType.STATIC,
            collision_method = CollisionMethod.PASSIVE,
            sensor = True,
            active_tags = [],
            passive_tags = [
                collision_tags.GRABBABLE
            ],
            shape = CollisionRect(
                anchor_x = 15,
                anchor_y = 15,
                width = 30,
                height = 30,
                batch = batch
            ),
            owner = self
        )
        self.add_component(self.__ground_sensor)
        self.add_component(self.__grab_trigger)
        controllers.COLLISION_CONTROLLER.add_collider(self.__collider)
        controllers.COLLISION_CONTROLLER.add_collider(self.__ground_sensor)
        controllers.COLLISION_CONTROLLER.add_collider(self.__grab_trigger)
        ################################
        ################################

    def __enter_water(self) -> None:
        self.in_water = True

        # Clear gravity vector on collision.
        self.target_gravity_speed = 0.0

    def __exit_water(self) -> None:
        self.in_water = False

        self.target_gravity_speed = math.inf

    def on_collision(self, tags: list[str], collider_id: int, entered: bool) -> None:
        if collision_tags.WATER not in tags:
            return

        # Remove vertical movement.
        self.move_vec = pm.Vec2(self.move_vec.x, 0.0)

        if entered:
            self.__enter_water()
        else:
            self.__exit_water()

        # Fix vertical gravity vector.
        self.gravity_vec = pm.Vec2(self.gravity_vec.x, -100.0)

    def on_ground_collision(self, tags: list[str], collider_id: int, entered: bool) -> None:
        if entered:
            self.__ground_collision_ids.add(collider_id)
        else:
            if collider_id in self.__ground_collision_ids:
                self.__ground_collision_ids.remove(collider_id)

        if len(self.__ground_collision_ids) > 0:
            self.grounded = True
        else:
            self.grounded = False

        # Clear gravity vector on collision.
        if self.grounded:
            self.gravity_vec *= 0.0

    def on_interactable_found(self, tags: list[str], collider: CollisionNode, entered: bool) -> None:
        if (collider.owner is not None):
            if entered:
                self.__interactables.add(collider.owner)
            else:
                self.__interactables.remove(collider.owner)

    def spawn_ink(self) -> None:
        ink_spawn_offset: pm.Vec2 = self.ink_offset * self.aim_vec
        self.ink = InkNode(
            x = self.x + ink_spawn_offset.x,
            y = self.y + ink_spawn_offset.y,
            z = self.z - 100,
            batch = self.__batch
        )

        if uniques.ACTIVE_SCENE is not None:
            uniques.ACTIVE_SCENE.add_child(self.ink)

    def delete_ink(self) -> None:
        if self.ink is None:
            return

        # First remove ink from the active scene.
        if uniques.ACTIVE_SCENE is not None:
            uniques.ACTIVE_SCENE.remove_child(self.ink)

        # Then delete the ink altogether.
        self.ink.delete()
        self.ink = None

    def move_ink(self) -> None:
        if self.ink is None:
            return

        ink_offset: pm.Vec2 = self.ink_offset * self.aim_vec
        self.ink.set_position((
            self.x + ink_offset.x,
            self.y + ink_offset.y
        ))

    def shoot_ink(self) -> None:
        if self.ink is None:
            return

        self.ink.release(self.aim_vec * self.shoot_force)
        self.ink = None

    def toggle_grab(self, toggle: bool) -> None:
        Grabbable.toggle_grab(self, toggle)

        if toggle:
            controllers.COLLISION_CONTROLLER.add_collider(self.__grab_trigger)
            self.__exit_water()
        else:
            controllers.COLLISION_CONTROLLER.remove_collider(self.__grab_trigger)

            # Clear gravity vector otherwise it builds up while being held.
            self.gravity_vec *= 0.0

    def interact(self) -> None:
        self.__interactor.interact()

    def get_move_dampening(self) -> float:
        return self.water_move_dampening if self.in_water else self.land_move_dampening

    def get_gravity_dampening(self) -> float:
        # return self.water_dampening if self.in_water else self.land_dampening
        return self.water_gravity_dampening if self.in_water else self.land_gravity_dampening

    def update(self, dt: float) -> None:
        super().update(dt = dt)

        # Compute facing direction from aim if any, otherwise from movement.
        dir_cos: float = math.cos(self.aim_vec.heading() if self.aim_vec.length() > 0.0 else self.move_vec.heading())
        dir_len: float = abs(dir_cos)

        # Only update facing if there's any horizontal movement.
        if dir_len > 0.1:
            self.__hor_facing = int(math.copysign(1.0, dir_cos))

        # Update interactor.
        self.__interactor.update(dt = dt)

        # Flip sprite if moving to the left.
        self.sprite.set_scale(x_scale = self.__hor_facing)

    def delete(self) -> None:
        self.delete_ink()
        self.__collider.delete()
        super().delete()

    def move_to(
        self,
        position: tuple[float, float]
    ):
        super().move_to(position = position)

        self.__collider.set_position(position = position)

    def set_animation(self, animation: Animation) -> None:
        self.sprite.set_image(animation.content)

    def compute_move_speed(
        self,
        move_vec: pyglet.math.Vec2,
        dt: float,
        max_speed: float | None = None,
    ) -> None:
        target_speed: float = 0.0
        target_heading: float = self.move_vec.heading()

        current_speed: float = self.move_vec.length()

        # Set target speed and heading from input move vector.
        if move_vec.length() > 0.0:
            target_speed = self.max_move_speed
            target_heading = move_vec.heading()

        if move_vec.length() < target_speed:
            # Accelerate when the current speed is lower than the target speed.
            current_speed += self.move_accel * self.get_move_dampening() * dt
        else:
            # Decelerate otherwise.
            current_speed -= self.move_accel * self.get_move_dampening() * dt

        self.move_vec = pm.Vec2.from_polar(
            length = pm.clamp(
                current_speed,
                0.0,
                (max_speed if max_speed is not None else self.max_move_speed) * self.get_move_dampening()
            ),
            angle = target_heading
        )

    def compute_gravity_speed(self, dt: float) -> None:
        if self.grounded:
            return

        if self.gravity_vec.length() < self.target_gravity_speed:
            # Accelerate when not grounded.
            self.gravity_vec += self.gravity_accel * self.get_gravity_dampening() * dt
        elif self.gravity_vec.length() > self.target_gravity_speed:
            # Gravity dampening is not applied during deceleration, in order to allow deceleration also when gravity dampening is 0.
            self.gravity_vec -= self.gravity_accel * self.get_gravity_dampening() * dt

            # Make sure to stop at 0.0.
            if self.gravity_vec.y > 0.0:
                self.gravity_vec *= 0.0

        self.gravity_vec = pm.Vec2.from_polar(
            length = round(self.gravity_vec.length(), GLOBALS[Keys.FLOAT_ROUNDING]),
            angle = self.gravity_vec.heading()
        )

    def move(self, dt: float) -> None:
        # Apply movement after collision.
        self.set_position(self.__collider.get_position())

        velocity: pm.Vec2 = self.move_vec

        if not self.grabbed:
            velocity += self.gravity_vec

        if velocity.length() > 0.0:
            self.heading = velocity.heading()

        # Compute and apply velocity for the next step.
        self.set_velocity(velocity = velocity)

    def set_velocity(self, velocity: pyglet.math.Vec2) -> None:
        # Apply the computed velocity to all colliders.
        converted_velocity: tuple[float, float] = (
            round(velocity.x, GLOBALS[Keys.FLOAT_ROUNDING]),
            round(velocity.y, GLOBALS[Keys.FLOAT_ROUNDING])
        )
        self.__collider.set_velocity(converted_velocity)