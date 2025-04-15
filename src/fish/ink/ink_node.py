import pyglet
import pyglet.math as pm

from amonite.node import PositionNode
from amonite.state_machine import StateMachine

from fish.ink.ink_data_node import InkDataNode
from fish.ink.states.ink_load_state import InkLoadState
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
            batch = batch
        )

        # State machine.
        self.__state_machine: StateMachine = StateMachine(
            states = {
                InkStates.LOAD: InkLoadState(actor = self.__data),
                InkStates.FLY: InkFlyState(actor = self.__data),
                # InkStates.SPLAT: FishDashState(actor = self.__data, input_enabled = enabled)
            }
        )

    def release(self, shoot_vec: pm.Vec2) -> None:
        """
        Sets the ink flying.
        """

        self.__data.set_shoot_vec(shoot_vec = shoot_vec)
        self.__state_machine.set_state(InkStates.FLY)

    def delete(self) -> None:
        self.__data.delete()

        return super().delete()

    def update(self, dt: float) -> None:
        super().update(dt = dt)
        
        self.__state_machine.update(dt = dt)

        self.__data.set_position(self.get_position())

        self.__data.update(dt = dt)

    def on_sprite_animation_end(self):
        self.__state_machine.on_animation_end()