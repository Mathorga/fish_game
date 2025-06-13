import os
import pyglet
import pyglet.gl as gl
import amonite.controllers as controllers
from amonite.upscaler import TrueUpscaler
from amonite.settings import GLOBALS, SETTINGS, Keys, load_settings

from constants import uniques
from mid_camera_node import MidCameraNode
from scene_composer import SceneComposerNode


FRAGMENT_SOURCE = """
    #version 150 core
    in vec4 vertex_colors;
    in vec3 texture_coords;
    out vec4 final_color;

    uniform sampler2D sprite_texture;
    uniform float dt;

    void main() {
        final_color = texture(sprite_texture, texture_coords.xy) * vertex_colors;

        // Dips to red on long rendered frames.
        //final_color.gb *= (1.0 - (dt - 0.01) * 100.0);

        // Rotate colors.
        //final_color.rgb = final_color.gbr;

        // Black/white.
        //float brightness = (final_color.r + final_color.g + final_color.b) / 3.0;
        //final_color = vec4(brightness, brightness, brightness, final_color.a);

        // Shows current xy coords on top of real colors.
        //final_color.rg *= texture_coords.xy;

        // Negative colors.
        //final_color.rgb = 1.0 - final_color.rgb;

        // This may be completely useless.
        if (final_color.a < 0.01) {
            discard;
        }
    }
"""
vert_shader = pyglet.graphics.shader.Shader(pyglet.sprite.vertex_source, "vertex")
frag_shader = pyglet.graphics.shader.Shader(FRAGMENT_SOURCE, "fragment")
upscaler_program = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

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
        platform_scaling: float = 0.5 if "macOS" in GLOBALS[Keys.PLATFORM] else 1.0

        # Compute pixel scaling (minimum unit is <1 / scaling>)
        # Using a scaling of 1 means that movements are pixel-perfect (aka nothing moves by sub-pixel values).
        # Using a scaling of 5 means that the minimum unit is 1/5 of a pixel.
        GLOBALS[Keys.SCALING] = 1 if SETTINGS[Keys.PIXEL_PERFECT] else int(min(
            self.__window.width // SETTINGS[Keys.VIEW_WIDTH],
            self.__window.height // SETTINGS[Keys.VIEW_HEIGHT]
        ) * platform_scaling)

        self.__upscaler = TrueUpscaler(
            window = self.__window,
            render_width = int((SETTINGS[Keys.VIEW_WIDTH] * GLOBALS[Keys.SCALING]) / platform_scaling),
            render_height = int((SETTINGS[Keys.VIEW_HEIGHT] * GLOBALS[Keys.SCALING]) / platform_scaling),
            program = upscaler_program
        )

        # Create a scene.
        uniques.ACTIVE_SCENE = SceneComposerNode(
            window = self.__window,
            view_width = SETTINGS[Keys.VIEW_WIDTH],
            view_height = SETTINGS[Keys.VIEW_HEIGHT],
            config_file_path = "scenes/0_0_0.json"
        ).scene

        uniques.ACTIVE_SCENE.add_child(
            MidCameraNode(
                targets = [
                    uniques.LEG,
                    uniques.FISH
                ]
            ),
            cam_target = True
        )


        ########################
        # Physics timestep.
        ########################
        self.phys_accumulated_time: float = 0.0
        self.phys_timestep: float = 1.0 / (SETTINGS[Keys.TARGET_FPS])
        ########################
        ########################

    def __create_window(self) -> pyglet.window.BaseWindow:
        window = pyglet.window.Window(
            width = SETTINGS[Keys.WINDOW_WIDTH] if not SETTINGS[Keys.FULLSCREEN] else None,
            height = SETTINGS[Keys.WINDOW_HEIGHT] if not SETTINGS[Keys.FULLSCREEN] else None,
            caption = SETTINGS[Keys.TITLE],
            fullscreen = SETTINGS[Keys.FULLSCREEN],
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

            # InputController makes sure every input is handled correctly.
            with controllers.INPUT_CONTROLLER:
                if uniques.ACTIVE_SCENE is not None:
                    uniques.ACTIVE_SCENE.update(dt = self.phys_timestep)

            # Compute collisions through collision manager.
            controllers.COLLISION_CONTROLLER.update(dt = self.phys_timestep)
            self.phys_accumulated_time -= self.phys_timestep

    def run(self) -> None:
        pyglet.clock.schedule_interval(self.update, 1.0 / (2.0 * SETTINGS[Keys.TARGET_FPS]))
        pyglet.app.run(interval =  1.0 / SETTINGS[Keys.TARGET_FPS])

FishGame().run()