from enum import Enum
from amonite.state_machine import State
from leg.land_leg.land_leg_data_node import LandLegDataNode

class LandLegStates(str, Enum):
    """
    All possible states for land leg.
    """

    IDLE = "idle"
    WALK = "swim"

class LandLegState(State):
    """
    Base class for land leg states.
    """

    def __init__(
        self,
        actor: LandLegDataNode
    ) -> None:
        super().__init__()

        self.input_enabled: bool = True
        self.actor: LandLegDataNode = actor

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