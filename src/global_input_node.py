import pyglet

from amonite.node import Node
import amonite.controllers as controllers

from constants import uniques
import scene_composer

class GlobalInputNode(Node):
    """
    Handles all inputs that's not for character handling (e.g. level restart, menu open, exit, etc.).
    """

    def __init__(self) -> None:
        super().__init__()

        self.__reset: bool = False

    def __fetch_input(self) -> None:
        self.__reset = controllers.INPUT_CONTROLLER.key_presses.get(pyglet.window.key.R, False)

    def update(self, dt):
        super().update(dt)

        # Fetch input.
        self.__fetch_input()

        # Reset the game.
        if self.__reset:
            if scene_composer.SCENE_COMPOSER is not None and uniques.ACTIVE_SCENE_SRC is not None:
                scene_composer.SCENE_COMPOSER.load_scene(uniques.ACTIVE_SCENE_SRC)
