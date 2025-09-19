from scene_composer import SCENE_COMPOSER
import os
import pyglet
import pyglet.gl as gl

import amonite.controllers as controllers
from amonite.upscaler import TrueUpscaler
from amonite.settings import GLOBALS
from amonite.settings import SETTINGS
from amonite.settings import Keys
from amonite.settings import load_settings

from constants import uniques
from global_input_node import GlobalInputNode
import scene_composer
from scene_composer import SceneComposer
from utils import utils


class FishGame:
    def __init__(self) -> None:
        # Set resources path.
        pyglet.resource.path = [f"{os.path.dirname(__file__)}/../assets"]
        pyglet.resource.reindex()

        pyglet.options.dpi_scaling = "stretch"

        # Load font files.
        pyglet.font.add_file(f"{pyglet.resource.path[0]}/fonts/I-pixel-u.ttf")
        pyglet.font.add_file(f"{pyglet.resource.path[0]}/fonts/rughai.ttf")

        # Load settings from file.
        load_settings(f"{pyglet.resource.path[0]}/settings.json")

        # Create a window.
        self.__window: pyglet.window.BaseWindow = self.__create_window()
        self.__fps_display = pyglet.window.FPSDisplay(
            window = self.__window,
            color = (0x00, 0x00, 0x00, 0xFF),
            samples = 16
        )

        # Controllers.
        controllers.create_controllers(window = self.__window)

        # On retina Macs everything is rendered 2x-zoomed for some reason. compensate for this using a platform scaling.
        platform_scaling: float = 0.5 if "macOS" in str(GLOBALS[Keys.PLATFORM]) else 1.0

        # Compute pixel scaling (minimum unit is <1 / scaling>)
        # Using a scaling of 1 means that movements are pixel-perfect (aka nothing moves by sub-pixel values).
        # Using a scaling of 5 means that the minimum unit is 1/5 of a pixel.
        GLOBALS[Keys.SCALING] = 1 if SETTINGS[Keys.PIXEL_PERFECT] else int(min(
            self.__window.width // int(SETTINGS[Keys.VIEW_WIDTH]),
            self.__window.height // int(SETTINGS[Keys.VIEW_HEIGHT])
        ) * platform_scaling)

        # Define a custom shader for global scene rendering.
        upscaler_program: pyglet.graphics.shader.ShaderProgram = utils.load_shader(
            vert_file_path = "shaders/default.vert.glsl",
            frag_file_path = "shaders/default.frag.glsl"
        )

        self.__upscaler = TrueUpscaler(
            window = self.__window,
            render_width = int((SETTINGS[Keys.VIEW_WIDTH] * GLOBALS[Keys.SCALING]) / platform_scaling),
            render_height = int((SETTINGS[Keys.VIEW_HEIGHT] * GLOBALS[Keys.SCALING]) / platform_scaling),
            program = upscaler_program
        )

        # Create a scene.
        scene_composer.SCENE_COMPOSER = SceneComposer(
            window = self.__window,
            view_width = int(SETTINGS[Keys.VIEW_WIDTH]),
            view_height = int(SETTINGS[Keys.VIEW_HEIGHT])
        )
        scene_composer.SCENE_COMPOSER.load_scene(config_file_path = "scenes/0_0_0.json")

        self.__global_input_node: GlobalInputNode = GlobalInputNode()


        ########################
        # Physics timestep.
        ########################
        self.phys_accumulated_time: float = 0.0
        self.phys_timestep: float = 1.0 / float((SETTINGS[Keys.TARGET_FPS]))
        ########################
        ########################

    def __create_window(self) -> pyglet.window.BaseWindow:
        window = pyglet.window.Window(
            width = int(SETTINGS[Keys.WINDOW_WIDTH]) if not SETTINGS[Keys.FULLSCREEN] else None,
            height = int(SETTINGS[Keys.WINDOW_HEIGHT]) if not SETTINGS[Keys.FULLSCREEN] else None,
            caption = str(SETTINGS[Keys.TITLE]),
            fullscreen = bool(SETTINGS[Keys.FULLSCREEN]),
            vsync = True,
            resizable = True
        )

        # Set the clear color (used when the window is cleared).
        gl.glClearColor(0.0, 0.0, 0.0, 1.0)

        window.push_handlers(self)
        if not SETTINGS[Keys.DEBUG]:
            window.set_mouse_visible(False)

        return window

    def on_draw(self) -> None:
        """
        Draws everything to the screen.
        """

        # Update window matrix.
        self.__window.projection = pyglet.math.Mat4.orthogonal_projection(
            left = 0,
            right = self.__window.width,
            bottom = 0,
            top = self.__window.height,
            # For some reason near and far planes are inverted in sign, so that -500 means 500 and 1024 means -1024.
            z_near = -3000,
            z_far = 3000
        )

        # Benchmark measures render time.
        self.__window.clear()

        # Upscaler handles maintaining the wanted output resolution.
        with self.__upscaler:
            if uniques.ACTIVE_SCENE is not None:
                uniques.ACTIVE_SCENE.draw()

            if SETTINGS[Keys.DEBUG]:
                self.__fps_display.draw()

    def update(self, dt: float) -> None:
        # upscaler_program["dt"] = dt

        self.phys_accumulated_time += dt

        # InputController makes sure every input is handled correctly.
        # with controllers.INPUT_CONTROLLER:
        #     if uniques.ACTIVE_SCENE is not None:
        #         uniques.ACTIVE_SCENE.update(dt = dt)

        # # Compute collisions through collision manager.
        # controllers.COLLISION_CONTROLLER.update(dt = dt)

        while self.phys_accumulated_time >= self.phys_timestep:
            # Check for scene change.
            if uniques.NEXT_SCENE_SRC is not None:
                if uniques.NEXT_SCENE_SRC != uniques.ACTIVE_SCENE_SRC:
                    scene_composer.SCENE_COMPOSER.load_scene(config_file_path = uniques.NEXT_SCENE_SRC)
                continue

            # InputController makes sure every input is handled correctly.
            with controllers.INPUT_CONTROLLER:
                if uniques.ACTIVE_SCENE is not None:
                    uniques.ACTIVE_SCENE.update(dt = self.phys_timestep)
                self.__global_input_node.update(dt = self.phys_timestep)

            # Compute collisions through collision manager.
            controllers.COLLISION_CONTROLLER.update(dt = self.phys_timestep)
            self.phys_accumulated_time -= self.phys_timestep

    def run(self) -> None:
        pyglet.clock.schedule_interval(self.update, 1.0 / (2.0 * float(SETTINGS[Keys.TARGET_FPS])))
        pyglet.app.run(interval =  1.0 / float(SETTINGS[Keys.TARGET_FPS]))

FishGame().run()