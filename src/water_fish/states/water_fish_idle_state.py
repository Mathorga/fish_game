from amonite.animation import Animation
from water_fish.water_fish_data_node import WaterFishDataNode
from water_fish.states.water_fish_state import WaterFishStates
from water_fish.states.water_fish_state import WaterFishState

class WaterFishIdleState(WaterFishState):
    def __init__(
        self,
        actor: WaterFishDataNode
    ) -> None:
        super().__init__(actor = actor)

        self.__animation: Animation = Animation(source = "sprites/fish_idle.json")

        # Inputs.
        self.__move: bool = False
        self.__dash: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move = self.actor.get_input_movement()
            self.__dash = self.actor.get_input_dash()

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        # Check for state changes.
        if self.__move:
            return WaterFishStates.SWIM

        if self.__dash:
            return WaterFishStates.DASH