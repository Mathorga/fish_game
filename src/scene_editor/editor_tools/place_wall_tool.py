from typing import Callable
import pyglet

from amonite.node import PositionNode
from amonite.shapes.rect_node import RectNode
from editor_tools.editor_tool import EditorTool
from amonite.utils.utils import point_in_rect
from amonite.wall_node import WALL_COLOR
from amonite.wall_node import WallNode
from amonite.utils.walls_loader import WallsLoader

from constants import collision_tags
from constants import uniques

TOOL_COLOR: tuple[int, int, int, int] = WALL_COLOR
ALT_COLOR: tuple[int, int, int, int] = (0xFF, 0x7F, 0x00, 0x7F)

class PlaceWallTool(EditorTool):
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
        self.name = "Place wall"
        self.color = TOOL_COLOR

        # Save data for later use.
        self.__tile_size: tuple[int, int] = tile_size
        self.__scene_name: str = scene_name
        self.__world_batch: pyglet.graphics.Batch | None = world_batch
        self.__ui_batch: pyglet.graphics.Batch | None = ui_batch

        # Area of the currently created
        self.__current_wall: RectNode | None = None

        # list of all inserted nodes.
        self.__walls: list[WallNode] = []
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
                    color = WALL_COLOR,
                    batch = self.__world_batch,
                )
            else:
                # Just return if there's no current wall.
                if self.__current_wall is None:
                    return

                # Create a wall with the given position and size.
                # The wall size is computed by subtracting the start position from the current.
                current_bounds: tuple[float, float, float, float] = self.__current_wall.get_bounds()
                wall: WallNode = WallNode(
                    x = current_bounds[0],
                    y = current_bounds[1],
                    width = int(current_bounds[2]),
                    height = int(current_bounds[3]),
                    tags = [collision_tags.PLAYER_COLLISION],
                    batch = self.__world_batch
                )

                # Save the newly created wall
                self.__walls.append(wall)

                if uniques.ACTIVE_SCENE is not None:
                    uniques.ACTIVE_SCENE.add_child(wall)

                # Reset the starting position.
                self.__starting_position = None

                # Delete the current wall.
                if self.__current_wall is not None:
                    self.__current_wall.delete()
                    self.__current_wall = None

        # Store the updated walls.
        WallsLoader.store(
            dest = f"{pyglet.resource.path[0]}/wallmaps/{self.__scene_name}.json",
            walls = self.__walls
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
            hit_walls: list[WallNode] = list(
                filter(
                    lambda wall: point_in_rect(
                        test = test_position,
                        rect_position = (wall.x, wall.y),
                        rect_size = (wall.width, wall.height)
                    ),
                    self.__walls
                )
            )

            # Delete any wall overlapping the current map_position.
            for wall in hit_walls:
                self.__walls.remove(wall)
                wall.delete()

    def __load_walls(self) -> None:
        # Delete all existing walls.
        for wall in self.__walls:
            if wall is not None:
                wall.delete()
        self.__walls.clear()

        # Recreate all of them from wallmap files.
        self.__walls = WallsLoader.fetch(
            source = f"wallmaps/{self.__scene_name}.json",
            batch = self.__world_batch
        )