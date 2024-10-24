import json
from typing import Any
import pyglet
from pyglet.window import BaseWindow
from amonite.node import Node
from amonite.scene_node import SceneNode

from fish.fish_node import FishNode

class SceneComposerNode():
    """
    Handles scene composition via file.
    Creates a new scene by reading a config file.
    """

    def __init__(
        self,
        window: BaseWindow,
        view_width: int,
        view_height: int,
        config_file_path: str
    ):
        # Read config file and setup the scene.
        self.config_data: dict[str, Any] = {}
        with open(file = f"{pyglet.resource.path[0]}/{config_file_path}", mode = "r", encoding = "UTF-8") as content:
            self.config_data = json.load(content)

        # Store all keys for faster access.
        config_keys: list[str] = list(self.config_data.keys())

        # Make sure all mandatory fields are present in the config file.
        assert "title" in config_keys and "children" in config_keys

        # Read scene title.
        self.title: str = self.config_data["title"]

        self.scene: SceneNode = SceneNode(
            window = window,
            view_width = view_width,
            view_height = view_height,
            title = self.title,
        )

        # Read children.
        self.children_data: list[dict[str, Any]] = self.config_data["children"]
        self.children: list[Node] = list(
            filter(
                # Only pick values that are not None.
                lambda item: item is not None,
                map(
                    # Map each element to a Node.
                    self.__map_child,
                    self.children_data
                )
            )
        )

        self.scene.add_children(self.children)

    def __map_child(self, child_data: dict[str, Any]) -> Node:
        assert "name" in child_data.keys()

        match child_data["name"]:
            case "fish_node":
                return FishNode(
                    x = child_data["x"],
                    y = child_data["y"],
                    batch = self.scene.world_batch
                )
            case "leg_node":
                return Node()
            case "tilemap":
                return Node()
            case _:
                # TODO Return something visible so that the user notices something's wrong.
                return Node()