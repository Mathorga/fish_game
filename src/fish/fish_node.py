import pyglet

from amonite.node import PositionNode
from amonite.state_machine import StateMachine

from fish.fish_data_node import FishDataNode
from fish.states.fish_state import FishStates
from fish.states.fish_crawl_state import FishCrawlState
from fish.states.fish_dash_state import FishDashState
from fish.states.fish_idle_state import FishIdleState
from fish.states.fish_swim_state import FishSwimState

class FishNode(PositionNode):
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
        self.__data: FishDataNode = FishDataNode(
            x = x,
            y = y,
            z = z,
            on_sprite_animation_end = self.on_sprite_animation_end,
            batch = batch
        )

        # State machine.
        self.__state_machine: StateMachine = StateMachine(
            states = {
                FishStates.IDLE: FishIdleState(actor = self.__data),
                FishStates.SWIM: FishSwimState(actor = self.__data),
                FishStates.DASH: FishDashState(actor = self.__data),
                FishStates.CRAWL: FishCrawlState(actor = self.__data)
            }
        )

    def update(self, dt: float) -> None:
        super().update(dt = dt)
        
        self.__state_machine.update(dt = dt)

        self.__data.update(dt = dt)

    def on_sprite_animation_end(self):
        self.__state_machine.on_animation_end()