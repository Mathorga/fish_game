import json
from typing import Any
import pyglet
from pyglet.window import BaseWindow
from amonite.node import Node
from amonite.scene_node import Bounds
from amonite.scene_node import SceneNode

from fish.fish_node import FishNode
from fish.water_fish.water_fish_node import WaterFishNode

class SceneComposerNode(Node):
    def __init__(
        self,
        window: BaseWindow,
        view_width: int,
        view_height: int,
        config_file_path: str
    ):
        super().__init__()

        # Read config file and setup the scene.
        self.config_data: dict[str, Any] = {}
        with open(file = f"{pyglet.resource.path[0]}/{config_file_path}", mode = "r", encoding = "UTF-8") as content:
            self.config_data = json.load(content)

        # Store all keys for faster access.
        config_keys: list[str] = self.config_data.keys()

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
        self.children: list[Node] = filter(
            # Only pick values that are not None.
            lambda item: item is not None,
            map(
                # Map each element to a Node.
                self.map_child,
                self.children_data
            )
        )

        self.scene.add_children(self.children)

    def map_child(self, child_data: dict[str, Any]) -> Node | None:
        assert "name" in child_data.keys()

        match child_data["name"]:
            case "fish_node":
                # return FishNode(
                #     x = child_data["x"],
                #     y = child_data["y"]
                # )
                return WaterFishNode(
                    x = child_data["x"],
                    y = child_data["y"],
                    batch = self.scene.world_batch
                )
            case "leg_node":
                return Node()
            case "tilemap":
                return Node()
            case _:
                return None