from enum import Enum
from amonite.state_machine import State
from water_fish.water_fish_data_node import WaterFishDataNode

class WaterFishStates(str, Enum):
    IDLE = "idle"
    SWIM = "swim"
    DASH = "dash"

class WaterFishState(State):
    def __init__(
        self,
        actor: WaterFishDataNode
    ) -> None:
        super().__init__()

        self.input_enabled: bool = True
        self.actor: WaterFishDataNode = actor

    def enable_input(self) -> None:
        """
        Enables all input reading.
        """

        self.input_enabled = True

    def disable_input(self) -> None:
        """
        Disables all input reading.
        """

        self.input_enabled = False