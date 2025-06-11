import pyglet
import pyglet.math as pm

from amonite.node import PositionNode
from amonite.state_machine import StateMachine

from constants import uniques
from fish.ink.ink_data_node import InkDataNode
from fish.ink.states.ink_load_state import InkLoadState
from fish.ink.states.ink_splat_state import InkSplatState
from fish.ink.states.ink_fly_state import InkFlyState
from fish.ink.states.ink_state import InkStates

class InkNode(PositionNode):
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

        # Data node, responsible for all content handling.
        self.__data: InkDataNode = InkDataNode(
            x = x,
            y = y,
            z = z,
            on_sprite_animation_end = self.on_sprite_animation_end,
            on_collision = self.on_collision,
            on_deletion = self.__remove_and_delete,
            batch = batch
        )

        # State machine.
        self.__state_machine: StateMachine = StateMachine(
            states = {
                InkStates.LOAD: InkLoadState(actor = self.__data),
                InkStates.FLY: InkFlyState(actor = self.__data),
                InkStates.SPLAT: InkSplatState(actor = self.__data)
            }
        )

    def release(self) -> None:
        """
        Sets the ink flying.
        """

        self.__state_machine.set_state(InkStates.FLY)

    def set_shoot_vec(self, shoot_vec: pm.Vec2) -> None:
        """
        Sets the ink's shoot vector.
        """

        self.__data.set_shoot_vec(shoot_vec = shoot_vec)

    def set_position(self, position: tuple[float, float], z: float | None = None):
        super().set_position(position, z)

        self.__data.set_position(
            position = position,
            z = z
        )

    def __remove_and_delete(self) -> None:
        if uniques.ACTIVE_SCENE is not None:
            uniques.ACTIVE_SCENE.remove_child(self)

        self.delete()

    def delete(self) -> None:
        self.__data.delete()

        return super().delete()

    def update(self, dt: float) -> None:
        super().update(dt = dt)

        # State machine can change data, so data's update should be performed BEFORE state machine's update.
        self.__data.update(dt = dt)

        self.__state_machine.update(dt = dt)

        self.x = self.__data.x
        self.y = self.__data.y

    def on_sprite_animation_end(self):
        self.__state_machine.on_animation_end()

    def on_collision(self, tags: list[str], collider_id: int, entered: bool):
        self.__state_machine.on_collision(tags = tags, enter = entered)