import pyglet
from amonite.node import PositionNode
from amonite.state_machine import StateMachine
from water_fish.states.water_fish_dash_state import WaterFishDashState
from water_fish.water_fish_data_node import WaterFishDataNode
from water_fish.states.water_fish_idle_state import WaterFishIdleState
from water_fish.states.water_fish_state import WaterFishStates
from water_fish.states.water_fish_swim_state import WaterFishSwimState

class WaterFishNode(PositionNode):
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
        self.__data: WaterFishDataNode = WaterFishDataNode(
            x = x,
            y = y,
            z = z,
            on_sprite_animation_end = self.on_sprite_animation_end,
            batch = batch
        )

        # State machine.
        self.__state_machine: StateMachine = StateMachine(
            states = {
                WaterFishStates.IDLE: WaterFishIdleState(actor = self.__data),
                WaterFishStates.SWIM: WaterFishSwimState(actor = self.__data),
                WaterFishStates.DASH: WaterFishDashState(actor = self.__data)
            }
        )

    def update(self, dt: float) -> None:
        super().update(dt = dt)
        
        self.__state_machine.update(dt = dt)

        self.__data.update(dt = dt)

    def on_sprite_animation_end(self):
        self.__state_machine.on_animation_end()