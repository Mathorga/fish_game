from enum import Enum

from amonite.state_machine import State

from fish.fish_data_node import FishDataNode

class FishStates(str, Enum):
    """
    All possible states for fish.
    """

    IDLE = "idle"
    SWIM = "swim"
    DASH = "dash"
    CRAWL = "crawl"

class FishState(State):
    """
    Base class for water fish states.
    """

    def __init__(
        self,
        actor: FishDataNode
    ) -> None:
        super().__init__()

        self.input_enabled: bool = True
        self.actor: FishDataNode = actor

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