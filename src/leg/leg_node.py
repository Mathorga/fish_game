from leg.states.leg_state import LegState
import pyglet

from amonite.node import PositionNode
from amonite.state_machine import StateMachine

from character_node import CharacterNode
from leg.leg_data_node import LegDataNode
from leg.states.leg_idle_state import LegIdleState
from leg.states.leg_jump_load_state import LegJumpLoadState
from leg.states.leg_jump_state import LegJumpState
from leg.states.leg_walk_state import LegWalkState
from leg.states.leg_state import LegStates

class LegNode(CharacterNode):
    """
    Handles
    """

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        enabled: bool = True,
        batch: pyglet.graphics.Batch | None = None
    ) -> None:
        super().__init__(
            x = x,
            y = y,
            z = z,
            enabled = enabled
        )

        # Data node, responsible for all content handling.
        self.__data: LegDataNode = LegDataNode(
            x = x,
            y = y,
            z = z,
            on_sprite_animation_end = self.on_sprite_animation_end,
            on_collision = self.on_collision,
            batch = batch
        )

        # State machine.
        self.__state_machine: StateMachine = StateMachine(
            states = {
                LegStates.IDLE: LegIdleState(actor = self.__data, input_enabled = enabled),
                LegStates.WALK: LegWalkState(actor = self.__data, input_enabled = enabled),
                LegStates.JUMP_LOAD: LegJumpLoadState(actor = self.__data, input_enabled = enabled),
                LegStates.JUMP: LegJumpState(actor = self.__data, input_enabled = enabled)
            }
        )

    def toggle(self):
        super().toggle()

        for state in self.__state_machine.states.values():
            if not isinstance(state, LegState):
                continue

            if state.input_enabled:
                state.disable_input()
            else:
                state.enable_input()

    def update(self, dt: float) -> None:
        super().update(dt = dt)
        
        self.__state_machine.update(dt = dt)

        self.__data.update(dt = dt)

        self.set_position(self.__data.get_position())

    def delete(self) -> None:
        self.__data.delete()

        super().delete()

    def on_sprite_animation_end(self) -> None:
        self.__state_machine.on_animation_end()

    def on_collision(self, tags: list[str], collider_id: int, entered: bool) -> None:
        self.__state_machine.on_collision(tags = tags, enter = entered)