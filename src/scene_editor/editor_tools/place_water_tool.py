from typing import Callable
import pyglet

from amonite import controllers
from amonite.node import Node, PositionNode
from amonite.shapes.rect_node import RectNode
from editor_tools.editor_tool import EditorTool
from amonite.text_node import TextNode
from amonite.utils.utils import point_in_rect

from constants import collision_tags
from constants import uniques

TOOL_COLOR: tuple[int, int, int, int] = (0x7F, 0x7F, 0xFF, 0x7F)
ALT_COLOR: tuple[int, int, int, int] = (0xFF, 0x7F, 0x00, 0x7F)

class WaterEditorMenuNode(Node):
    def __init__(
        self,
        wall_names: list[str],
        view_width: int,
        view_height: int,
        start_open: bool = False,
        batch: pyglet.graphics.Batch | None = None,
    ) -> None:
        super().__init__()

        self.__wall_names = wall_names
        self.__view_width = view_width
        self.__view_height = view_height
        self.__batch = batch

        # Flag, defines whether the menu is open or close.
        self.__open = start_open

        # Elements in the current page.
        self.__wall_texts: list[TextNode] = []

        # Currently selected element.
        self.__current_index: int = 0

        self.__background: RectNode | None = None

    def update(self, dt: int) -> None:
        super().update(dt)

        if self.__open:
            # Only handle controls if open:
            # Wall selection.
            self.__current_index -= int(controllers.INPUT_CONTROLLER.get_cursor_movement_vec(
                up_keys = [pyglet.window.key.W],
                left_keys = [pyglet.window.key.A],
                down_keys = [pyglet.window.key.S],
                right_keys = [pyglet.window.key.D],
            ).y)
            if self.__current_index < 0:
                self.__current_index = 0
            if self.__current_index >= len(self.__wall_names):
                self.__current_index = len(self.__wall_names) - 1

    def get_current_prop(self) -> str:
        return self.__wall_names[self.__current_index]

    def is_open(self) -> bool:
        return self.__open

    def open(self) -> None:
        self.__open = True

        self.__background = RectNode(
            x = 0.0,
            y = 0.0,
            z = -100.0,
            width = self.__view_width,
            height = self.__view_height,
            color = (0x33, 0x33, 0x33, 0xFF),
            batch = self.__batch
        )
        self.__background.set_opacity(0xDD)

    def close(self) -> None:
        self.__open = False

        if self.__background is not None:
            self.__background.delete()
            self.__background = None

class PlaceWaterTool(EditorTool):
    def __init__(
        self,
        view_width: int,
        view_height: int,
        tile_size: tuple[int, int],
        scene_name: str,
        on_icon_changed: Callable | None = None,
        world_batch: pyglet.graphics.Batch | None = None,
        ui_batch: pyglet.graphics.Batch | None = None
    ) -> None:
        super().__init__(
            on_icon_changed = on_icon_changed
        )

        # Parent overrides.
        self.name = "Place water"
        self.color = TOOL_COLOR

        # Save data for later use.
        self.__tile_size: tuple[int, int] = tile_size
        self.__scene_name: str = scene_name
        self.__world_batch: pyglet.graphics.Batch | None = world_batch
        self.__ui_batch: pyglet.graphics.Batch | None = ui_batch

        # Create a menu to handle wall type selection.
        self.__menu = WaterEditorMenuNode(
            wall_names = [],
            view_width = view_width,
            view_height = view_height,
            batch = ui_batch
        )

        # Area of the currently created
        self.__current_wall: RectNode | None = None

        # list of all inserted nodes.
        self.__waters: list[HittableNode] = []
        self.__load_walls()

        # Starting position of the wall currently being placed.
        self.__starting_position: tuple[int, int] | None = None

    def move_cursor(self, map_position: tuple[int, int]) -> None:
        super().move_cursor(map_position)

        if self.__current_wall is not None and self.__starting_position is not None:
            # current_bounds: tuple[float, float, float, float] = self.__current_wall.get_bounds()
            self.__current_wall.set_bounds(
                bounds = (
                    # X position.
                    min(map_position[0], self.__starting_position[0]) * self.__tile_size[0],
                    # Y position.
                    min(map_position[1], self.__starting_position[1]) * self.__tile_size[1],
                    # Width.
                    (abs(map_position[0] - self.__starting_position[0]) + 1.0) * self.__tile_size[0],
                    # Height.
                    (abs(map_position[1] - self.__starting_position[1]) + 1.0) * self.__tile_size[1]
                )
            )

    def get_cursor_icon(self) -> PositionNode:
        # Return a tile-sized rectangle. It's color depends on whether alternate mode is on or off.
        return RectNode(
            x = 0.0,
            y = 0.0,
            width = self.__tile_size[0],
            height = self.__tile_size[1],
            anchor_x = self.__tile_size[0] / 2,
            anchor_y = self.__tile_size[1] / 2,
            color = ALT_COLOR if self.alt_mode else self.color,
            batch = self.__world_batch
        )

    def toggle_menu(self, toggle: bool) -> None:
        return super().toggle_menu(toggle = toggle)

    def toggle_alt_mode(self, toggle: bool) -> None:
        super().toggle_alt_mode(toggle)

        # Notify icon changed.
        if self.on_icon_changed is not None:
            self.on_icon_changed()

    def run(self, map_position: tuple[int, int]) -> None:
        super().run(map_position = map_position)

        if self.alt_mode:
            self.clear(map_position = map_position)
        else:
            if self.__starting_position == None:
                # Record starting position.
                self.__starting_position = map_position

                # Create the rect node for displaying the area currently being defined.
                self.__current_wall = RectNode(
                    x = map_position[0] * self.__tile_size[0],
                    y = map_position[1] * self.__tile_size[1],
                    width = self.__tile_size[0],
                    height = self.__tile_size[1],
                    color = TOOL_COLOR,
                    batch = self.__world_batch,
                )
            else:
                # Just return if there's no current wall.
                if self.__current_wall is None:
                    return

                # Create a wall with the given position and size.
                # The wall size is computed by subtracting the start position from the current.
                current_bounds: tuple[float, float, float, float] = self.__current_wall.get_bounds()
                water: HittableNode = HittableNode(
                    x = current_bounds[0],
                    y = current_bounds[1],
                    width = int(current_bounds[2]),
                    height = int(current_bounds[3]),
                    tags = [collision_tags.PLAYER_SENSE],
                    sensor = True,
                    batch = self.__world_batch
                )

                # Save the newly created wall
                self.__waters.append(water)

                if uniques.ACTIVE_SCENE is not None:
                    uniques.ACTIVE_SCENE.add_child(water)

                # Reset the starting position.
                self.__starting_position = None

                # Delete the current wall.
                if self.__current_wall is not None:
                    self.__current_wall.delete()
                    self.__current_wall = None

        # Store the updated walls.
        HittablesLoader.store(
            dest = f"{pyglet.resource.path[0]}/watermaps/{self.__scene_name}.json",
            hittables = self.__waters
        )

    def clear(self, map_position: tuple[int, int]) -> None:
        """
        Deletes any wall overlapping the provided map position, regardless of the selected wall tags.
        """

        # Delete the current wall if any.
        if self.__current_wall is not None:
            self.__current_wall.delete()
            self.__current_wall = None
            self.__starting_position = None
        else:
            # Define a test position at the center of a tile.
            test_position: tuple[float, float] = (
                map_position[0] * self.__tile_size[0] + self.__tile_size[0] / 2,
                map_position[1] * self.__tile_size[1] + self.__tile_size[1] / 2
            )

            # Filter overlapping walls.
            hit_waters: list[HittableNode] = list(
                filter(
                    lambda water: point_in_rect(
                        test = test_position,
                        rect_position = (water.x, water.y),
                        rect_size = (water.width, water.height)
                    ),
                    self.__waters
                )
            )

            # Delete any wall overlapping the current map_position.
            for wall in hit_waters:
                self.__waters.remove(wall)
                wall.delete()

    def __load_walls(self) -> None:
        # Delete all existing walls.
        for wall in self.__waters:
            if wall is not None:
                wall.delete()
        self.__waters.clear()

        # Recreate all of them from wallmap files.
        self.__waters = HittablesLoader.fetch(
            source = f"watermaps/{self.__scene_name}.json",
            sensor = True,
            batch = self.__world_batch
        )