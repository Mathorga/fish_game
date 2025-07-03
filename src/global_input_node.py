import pyglet

from amonite.node import Node
import amonite.controllers as controllers
from amonite.settings import SETTINGS

from constants import uniques
from constants import custom_setting_keys
import scene_composer

class GlobalInputNode(Node):
    """
    Handles all inputs that's not for character handling (e.g. level restart, menu open, exit, etc.).
    """

    def __init__(self) -> None:
        super().__init__()

        self.__reset: bool = False
        self.__switch: bool = False

    def __fetch_input(self) -> None:
        self.__reset = controllers.INPUT_CONTROLLER.key_presses.get(pyglet.window.key.R, False)

        # Only read character switch input if in single player mode.
        if SETTINGS[custom_setting_keys.SINGLE_PLAYER]:
            self.__switch = controllers.INPUT_CONTROLLER.key_presses.get(pyglet.window.key.TAB, False)

    def __reset_scene(self) -> None:
        if scene_composer.SCENE_COMPOSER is None:
            return

        if uniques.ACTIVE_SCENE_SRC is not None:
            scene_composer.SCENE_COMPOSER.load_scene(uniques.ACTIVE_SCENE_SRC)

    def __switch_characters(self) -> None:
        if uniques.FISH is None or uniques.LEG is None:
            return
        
        uniques.FISH.toggle()
        uniques.LEG.toggle()

    def update(self, dt) -> None:
        super().update(dt)

        # Fetch input.
        self.__fetch_input()

        # Reset the game.
        if self.__reset:
            self.__reset_scene()

        if self.__switch:
            self.__switch_characters()
