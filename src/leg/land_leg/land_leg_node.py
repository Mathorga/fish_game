import pyglet
from amonite.node import PositionNode
from amonite.state_machine import StateMachine
from leg.land_leg.land_leg_data_node import LandLegDataNode
from leg.land_leg.states.land_leg_idle_state import LandLegIdleState
from leg.land_leg.states.land_leg_jump_load_state import LandLegJumpLoadState
from leg.land_leg.states.land_leg_jump_state import LandLegJumpState
from leg.land_leg.states.land_leg_walk_state import LandLegWalkState
from leg.land_leg.states.land_leg_state import LandLegStates

class LandLegNode(PositionNode):
    """
    Handles
    """

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
        self.__data: LandLegDataNode = LandLegDataNode(
            x = x,
            y = y,
            z = z,
            on_sprite_animation_end = self.on_sprite_animation_end,
            batch = batch
        )

        # State machine.
        self.__state_machine: StateMachine = StateMachine(
            states = {
                LandLegStates.IDLE: LandLegIdleState(actor = self.__data),
                LandLegStates.WALK: LandLegWalkState(actor = self.__data),
                LandLegStates.JUMP_LOAD: LandLegJumpLoadState(actor = self.__data),
                LandLegStates.JUMP: LandLegJumpState(actor = self.__data),
            }
        )

    def update(self, dt: float) -> None:
        super().update(dt = dt)
        
        self.__state_machine.update(dt = dt)

        self.__data.update(dt = dt)

    def on_sprite_animation_end(self):
        self.__state_machine.on_animation_end()