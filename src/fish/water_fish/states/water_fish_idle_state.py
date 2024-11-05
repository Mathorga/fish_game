from amonite.animation import Animation
import amonite.controllers as controllers
from fish.water_fish.water_fish_data_node import WaterFishDataNode
from fish.water_fish.states.water_fish_state import WaterFishStates
from fish.water_fish.states.water_fish_state import WaterFishState

class WaterFishIdleState(WaterFishState):
    def __init__(
        self,
        actor: WaterFishDataNode
    ) -> None:
        super().__init__(actor = actor)

        self.__animation: Animation = Animation(source = "sprites/fish/water_fish/water_fish_idle.json")
        # self.__animation: Animation = Animation(source = "sprites/fish/water_fish/dumbo_water_idle.json")

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
            self.__move = controllers.INPUT_CONTROLLER.get_movement()
            self.__dash = controllers.INPUT_CONTROLLER.get_sprint()

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        # Check for state changes.
        if self.__move:
            return WaterFishStates.SWIM

        if self.__dash:
            return WaterFishStates.DASH