from enum import Enum
from amonite.state_machine import State
from leg.leg_data_node import LegDataNode

class LegStates(str, Enum):
    """
    All possible states for land leg.
    """

    IDLE = "idle"
    WALK = "walk"
    JUMP_LOAD = "jump_load"
    JUMP = "jump"

class LegState(State):
    """
    Base class for land leg states.
    """

    def __init__(
        self,
        actor: LegDataNode
    ) -> None:
        super().__init__()

        self.input_enabled: bool = True
        self.actor: LegDataNode = actor

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