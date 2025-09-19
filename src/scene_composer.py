
import json
from typing import Any
import pyglet
from pyglet.graphics import Batch
from pyglet.window import BaseWindow

import amonite.controllers as controllers
from amonite.animation import Animation
from amonite.sprite_node import SpriteNode
from amonite.scene_node import Bounds
from amonite.node import Node
from amonite.shapes.rect_node import RectNode
from amonite.scene_node import SceneNode
from amonite.tilemap_node import TilemapNode
from amonite.utils.hittables_loader import HittableNode
from amonite.utils.hittables_loader import HittablesLoader
from amonite.settings import SETTINGS

from constants import custom_setting_keys
from constants import uniques
from fish.fish_node import FishNode
from ink_button_node import Direction, InkButtonNode
from leg.leg_node import LegNode
from press_button_node import PressButtonNode
from red_platform_node import RedPlatformNode
from mid_camera_node import MidCameraNode
from door.door_node import DoorNode

class WaterHittableNode(HittableNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0,
        width: int = 8,
        height: int = 8,
        sensor: bool = False,
        color: tuple[int, int, int, int] = (0x7F, 0xDF, 0xFF, 0x7F),
        tags: list[str] | None = None,
        batch: Batch | None = None
    ) -> None:
        super().__init__(
            x = x,
            y = y,
            z = z,
            width = width,
            height = height,
            sensor = sensor,
            color = color,
            tags = tags,
            batch = batch
        )

        self.shape: RectNode = RectNode(
            x = x,
            y = y,
            z = z,
            width = width,
            height = height,
            color = color,
            batch = batch
        )

    @staticmethod
    def from_hittable(
        hittable: HittableNode,
        z: float | None = None,
        batch: Batch | None = None
    ):
        return WaterHittableNode(
            x = hittable.x,
            y = hittable.y,
            z = z if z is not None else hittable.z,
            width = hittable.width,
            height = hittable.height,
            tags = hittable.tags,
            sensor = hittable.sensor,
            batch = batch
        )

class SceneComposer():
    """
    Handles scene composition via file.
    Creates a new scene by reading a config file.
    """

    def __init__(
        self,
        window: BaseWindow,
        view_width: int,
        view_height: int
    ):
        self.__window: BaseWindow = window
        self.__view_width: int = view_width
        self.__view_height: int = view_height

        self.children: dict[tuple[str, int], Node] = {}
        self.scene: SceneNode

    def load_scene(self, config_file_path: str) -> None:
        """
        Loads all scene data from the provided scene config file.
        Destroys the currently active scene in the process.
        """

        # Delete any previous active scene.
        if uniques.ACTIVE_SCENE is not None:
            controllers.COLLISION_CONTROLLER.clear()
            uniques.ACTIVE_SCENE.delete()
            uniques.ACTIVE_SCENE = None

        # Store the currently open scene file.
        uniques.ACTIVE_SCENE_SRC = config_file_path

        # Read config file and setup the scene.
        with open(file = f"{pyglet.resource.path[0]}/{config_file_path}", mode = "r", encoding = "UTF-8") as content:
            config_data = json.load(content)

        # Store all keys for faster access.
        config_keys: list[str] = list(config_data.keys())

        # Make sure all mandatory fields are present in the config file.
        assert "title" in config_keys and "children" in config_keys

        # Read scene title.
        title: str = config_data["title"]

        ################################
        # Create scene.
        ################################
        self.scene = SceneNode(
            window = self.__window,
            view_width = self.__view_width,
            view_height = self.__view_height,
            curtain_z = 300.0,
            title = title,
        )
        ################################
        ################################

        ################################
        # Read tilemap.
        ################################
        tilemaps: list[TilemapNode] = TilemapNode.from_tmx_file(
            source = config_data["tilemap"],
            tilesets_path = "tilesets/",
            batch = self.scene.world_batch
        )
        tile_size: int = tilemaps[0].get_tile_size()[0]
        tilemap_width: int = tilemaps[0].map_width
        tilemap_height: int = tilemaps[0].map_height
        cam_bounds: Bounds = tilemaps[0].bounds
        ################################
        ################################

        ################################
        # Read children.
        ################################
        children_data: list[dict[str, Any]] = config_data["children"]
        self.children = {
            (child["name"], child["id"]): self.__map_child(child)
            for child in children_data
        }
        ################################
        ################################

        ################################
        # Read hittables.
        ################################
        __waters: list[WaterHittableNode] = []
        if config_data["waters"] is not None:
            __waters = list(
                map(
                    lambda hittable: WaterHittableNode.from_hittable(
                        hittable = hittable,
                        z = -200,
                        batch = self.scene.world_batch
                    ),
                    HittablesLoader.fetch(
                        source = config_data["waters"],
                        batch = self.scene.world_batch
                    )
                )
            )
        __walls: list[HittableNode] = []
        if config_data["walls"] is not None:
            __walls = HittablesLoader.fetch(
                source = config_data["walls"],
                batch = self.scene.world_batch
            )
        ################################
        ################################

        self.scene.add_children(tilemaps)
        self.scene.add_children([*self.children.values()])
        self.scene.add_children(__waters)
        self.scene.add_children(__walls)

        # Set scene cam bounds.
        self.scene.set_cam_bounds(bounds = cam_bounds)

        # Add a mid camera node between the two characters if defined in the current scene.
        if uniques.LEG is not None and uniques.FISH is not None:
            self.scene.add_child(
                MidCameraNode(
                    targets = [
                        uniques.LEG,
                        uniques.FISH
                    ]
                ),
                cam_target = True
            )

        uniques.ACTIVE_SCENE = self.scene
        uniques.NEXT_SCENE_SRC = None

    def __trigger_child(self, action: str, target_child_id: tuple[str, int]) -> None:
        """
        Triggers the child with the provided id.
        """

        # Make sure the target child exists.
        if not target_child_id in self.children.keys():
            return

        # Retrieve target child from its identifier.
        target_child: Node = self.children[target_child_id]

        # Make sure the target child exposes the method specified by [action].
        if not hasattr(target_child, action):
            return

        # Call the method on the target child.
        getattr(target_child, action)()

    def __on_child_triggered(self, data: list[dict[str, Any]] | None) -> None:
        """
        Handles reactions to children being triggered on or off.
        """

        # Just return if no data is provided.
        if data is None:
            return

        for element in data:
            # Make sure the proper action structure is ensured.
            if list(element.keys()) != ["action", "name", "id"]:
                continue

            # Extract target identifier.
            target_id: tuple[str, int] = (element["name"], element["id"])

            self.__trigger_child(element["action"], target_id)

    def __map_child(self, child_data: dict[str, Any]) -> Node:
        assert "name" in child_data.keys()

        # Read on trigger data.
        on_trigger_on_data: list[dict[str, Any]] | None = child_data["on_triggered_on"] if "on_triggered_on" in child_data.keys() else None
        on_trigger_off_data: list[dict[str, Any]] | None = child_data["on_triggered_off"] if "on_triggered_off" in child_data.keys() else None

        match child_data["name"]:
            case "fish_node":
                uniques.FISH = FishNode(
                    x = child_data["x"],
                    y = child_data["y"],
                    enabled = not SETTINGS[custom_setting_keys.SINGLE_PLAYER],
                    batch = self.scene.world_batch
                )
                return uniques.FISH
            case "leg_node":
                uniques.LEG = LegNode(
                    x = child_data["x"],
                    y = child_data["y"],
                    enabled = True,
                    batch = self.scene.world_batch
                )
                return uniques.LEG
            case "door":
                return DoorNode(
                    x = child_data["x"],
                    y = child_data["y"],
                    width = child_data["width"] if "width" in child_data else 0,
                    height = child_data["height"] if "height" in child_data else 0,
                    anchor_x = child_data["anchor_x"] if "anchor_x" in child_data else 0,
                    anchor_y = child_data["anchor_y"] if "anchor_y" in child_data else 0,
                    destination = child_data["destination"] if "destination" in child_data else None,
                    # Set room to the specified destination one.
                    on_triggered = lambda tags, collider, entered: print("nano"),
                    batch = self.scene.world_batch
                )
            case "ink_button_node":
                return InkButtonNode(
                    x = child_data["x"],
                    y = child_data["y"],
                    button_anchor = next((direction for direction in Direction if direction.value == child_data["button_anchor"]), Direction.DONW),
                    allow_turning_off = child_data["allow_turning_off"] if "allow_turning_off" in child_data else True,
                    on_triggered_on = lambda : self.__on_child_triggered(data = on_trigger_on_data),
                    on_triggered_off = lambda : self.__on_child_triggered(data = on_trigger_off_data),
                    batch = self.scene.world_batch
                )
            case "press_button_node":
                return PressButtonNode(
                    x = child_data["x"],
                    y = child_data["y"],
                    allow_turning_off = child_data["allow_turning_off"] if "allow_turning_off" in child_data else True,
                    on_triggered_on = lambda : self.__on_child_triggered(data = on_trigger_on_data),
                    on_triggered_off = lambda : self.__on_child_triggered(data = on_trigger_off_data),
                    batch = self.scene.world_batch
                )
            case "red_platform_node":
                return RedPlatformNode(
                    x = child_data["x"],
                    y = child_data["y"],
                    starts_on = child_data["starts_on"] if "starts_on" in child_data else False,
                    batch = self.scene.world_batch
                )
            case "tilemap":
                return Node()
            case _:
                # TODO Return something visible so that the user notices something's wrong.
                return Node()

SCENE_COMPOSER: SceneComposer | None = None