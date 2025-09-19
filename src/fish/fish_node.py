from fish.states.fish_state import FishState
import pyglet

from amonite.node import PositionNode
from amonite.state_machine import StateMachine

from character_node import CharacterNode
from fish.fish_data_node import FishDataNode
from fish.states.fish_shoot_load_state import FishShootLoadState
from fish.states.fish_shoot_state import FishShootState
from fish.states.fish_state import FishStates
from fish.states.fish_crawl_state import FishCrawlState
from fish.states.fish_dash_state import FishDashState
from fish.states.fish_idle_state import FishIdleState
from fish.states.fish_swim_state import FishSwimState

class FishNode(CharacterNode):
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
                FishStates.IDLE: FishIdleState(actor = self.__data, input_enabled = enabled),
                FishStates.SWIM: FishSwimState(actor = self.__data, input_enabled = enabled),
                FishStates.DASH: FishDashState(actor = self.__data, input_enabled = enabled),
                FishStates.CRAWL: FishCrawlState(actor = self.__data, input_enabled = enabled),
                FishStates.SHOOT_LOAD: FishShootLoadState(actor = self.__data, input_enabled = enabled),
                FishStates.SHOOT: FishShootState(actor = self.__data, input_enabled = enabled)
            }
        )

    def toggle(self):
        super().toggle()

        for state in self.__state_machine.states.values():
            if not isinstance(state, FishState):
                continue

            if state.input_enabled:
                state.disable_input()
            else:
                state.enable_input()

    def enable(self):
        super().enable()

        for state in self.__state_machine.states.values():
            if not isinstance(state, FishState):
                continue

            state.enable_input()

    def disable(self):
        super().disable()

        for state in self.__state_machine.states.values():
            if not isinstance(state, FishState):
                continue

            state.disable_input()

    def delete(self):
        self.__data.delete()

        super().delete()

    def update(self, dt: float) -> None:
        super().update(dt = dt)
        
        self.__state_machine.update(dt = dt)

        self.__data.update(dt = dt)

        self.set_position(self.__data.get_position())

    def on_sprite_animation_end(self):
        self.__state_machine.on_animation_end()