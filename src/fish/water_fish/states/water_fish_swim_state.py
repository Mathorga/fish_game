import pyglet
from amonite.animation import Animation
import amonite.controllers as controllers
from fish.water_fish.water_fish_data_node import WaterFishDataNode
from fish.water_fish.states.water_fish_state import WaterFishState
from fish.water_fish.states.water_fish_state import WaterFishStates

class WaterFishSwimState(WaterFishState):
    def __init__(
        self,
        actor: WaterFishDataNode
    ) -> None:
        super().__init__(actor = actor)

        # Animation.
        self.__animation: Animation = Animation(source = "sprites/fish/water_fish/water_fish_swim.json")

        # Input.
        self.__move_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__dash: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move_vec = controllers.INPUT_CONTROLLER.get_movement_vec()
            self.__dash = controllers.INPUT_CONTROLLER.get_sprint()

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        self.actor.compute_speed(move_vec = self.__move_vec, dt = dt)

        # Move the player.
        self.actor.move(dt = dt)

        # Check for state changes.
        if self.__dash:
            return WaterFishStates.DASH

        if self.actor.speed <= 0.0:
            return WaterFishStates.IDLE