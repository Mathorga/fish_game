from enum import Enum

from amonite.state_machine import State

from fish.ink.ink_data_node import InkDataNode

class InkStates(str, Enum):
    """
    All possible states for ink.
    """

    LOAD = "load"
    FLY = "swim"
    SPLAT = "dash"

class InkState(State):
    """
    Base class for ink states.
    """

    def __init__(
        self,
        actor: InkDataNode,
        input_enabled: bool = True
    ) -> None:
        super().__init__()

        self.input_enabled: bool = input_enabled
        self.actor: InkDataNode = actor

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