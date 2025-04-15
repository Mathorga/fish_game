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
    ) -> None:
        super().__init__()

        self.actor: InkDataNode = actor