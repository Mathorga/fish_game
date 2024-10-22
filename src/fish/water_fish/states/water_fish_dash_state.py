from amonite.animation import Animation
from fish.water_fish.water_fish_data_node import WaterFishDataNode
from fish.water_fish.states.water_fish_state import WaterFishStates
from fish.water_fish.states.water_fish_state import WaterFishState

class WaterFishDashState(WaterFishState):
    def __init__(
        self,
        actor: WaterFishDataNode
    ) -> None:
        super().__init__(actor = actor)

        # Animation.
        self.__animation: Animation = Animation(source = "sprites/fish_dash.json")
        self.__startup: bool = False
        self.__animation_ended: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.__startup = True
        self.__animation_ended = False

    def update(self, dt: float) -> str | None:
        # Handle animation end.
        if self.__animation_ended:
            if self.actor.speed <= 0.0:
                return WaterFishStates.IDLE
            else:
                return WaterFishStates.SWIM

        if self.__startup:
            self.actor.speed = self.actor.max_speed * 2
            self.__startup = False
        else:
            self.actor.speed -= (self.actor.accel / 2) * dt

        # Move the player.
        self.actor.move(dt = dt)

        # Check for state changes.
        if self.actor.speed <= 0.0:
            return WaterFishStates.IDLE

    def on_animation_end(self) -> None:
        self.__animation_ended = True