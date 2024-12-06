import json
from typing import Any
import pyglet
from pyglet.window import BaseWindow

from amonite.node import Node
from amonite.node import PositionNode
from amonite.scene_node import SceneNode
from amonite.tilemap_node import TilemapNode
from amonite.wall_node import WallNode
from amonite.utils.walls_loader import WallsLoader
from amonite.utils.hittables_loader import HittableNode
from amonite.utils.hittables_loader import HittablesLoader

from fish.fish_node import FishNode
from leg.leg_node import LegNode

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

        ################ Read tilemap ################
        tilemaps: list[TilemapNode] = TilemapNode.from_tmx_file(
            source = self.config_data["tilemap"],
            tilesets_path = "tilesets/",
            batch = self.scene.world_batch
        )
        self.__tile_size = tilemaps[0].get_tile_size()[0]
        tilemap_width = tilemaps[0].map_width
        tilemap_height = tilemaps[0].map_height
        cam_bounds = tilemaps[0].bounds

        ################################
        # Read children.
        ################################
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
        ################################
        ################################


        ################################
        # Read hittables.
        ################################
        self.__waters: list[HittableNode] = []
        if self.config_data["waters"] is not None:
            self.__waters = HittablesLoader.fetch(
                source = self.config_data["waters"],
                sensor = True,
                batch = self.scene.world_batch
            )
        self.__walls: list[HittableNode] = []
        if self.config_data["walls"] is not None:
            self.__walls = HittablesLoader.fetch(
                source = self.config_data["walls"],
                batch = self.scene.world_batch
            )

        ################################
        ################################

        self.scene.add_children(tilemaps)
        self.scene.add_children(self.children)
        self.scene.add_children(self.__waters)
        self.scene.add_children(self.__walls)

        # Add a camera target.
        self.scene.add_child(
            PositionNode(
                x = 500.0,
                y = 200.0
            ),
            cam_target = True
        )

    def __map_child(self, child_data: dict[str, Any]) -> Node:
        assert "name" in child_data.keys()

        match child_data["name"]:
            # case "fish_node":
            #     return FishNode(
            #         x = child_data["x"],
            #         y = child_data["y"],
            #         batch = self.scene.world_batch
            #     )
            case "leg_node":
                return LegNode(
                    x = child_data["x"],
                    y = child_data["y"],
                    batch = self.scene.world_batch
                )
            case "tilemap":
                return Node()
            case _:
                # TODO Return something visible so that the user notices something's wrong.
                return Node()