import os
import pyglet
import pyglet.gl as gl
import amonite.controllers as controllers
from amonite.animation import Animation
from amonite.upscaler import TrueUpscaler
from amonite.scene_node import SceneNode
from amonite.shapes.rect_node import RectNode
from amonite.sprite_node import SpriteNode
from amonite.node import PositionNode
from amonite.settings import GLOBALS, SETTINGS, Keys, load_settings

from constants import uniques
from fish.water_fish.water_fish_node import WaterFishNode
from scene_composer_node import SceneComposerNode


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
        # uniques.ACTIVE_SCENE = SceneNode(
        #     window = self.__window,
        #     view_width = SETTINGS[Keys.VIEW_WIDTH],
        #     view_height = SETTINGS[Keys.VIEW_HEIGHT],
        #     default_cam_speed = SETTINGS[Keys.CAMERA_SPEED],
        #     title = "fish_game"
        # )
        uniques.ACTIVE_SCENE = SceneComposerNode(
            window = self.__window,
            view_width = SETTINGS[Keys.VIEW_WIDTH],
            view_height = SETTINGS[Keys.VIEW_HEIGHT],
            config_file_path = "scenes/0_0_0.json"
        ).scene

        ######################## Scene content ########################

        # test_sprite: PositionNode = SpriteNode(
        #     resource = Animation(source = "sprites/fish_idle.json").content,
        #     x = SETTINGS[Keys.VIEW_WIDTH] / 2,
        #     y = SETTINGS[Keys.VIEW_HEIGHT] / 2,
        #     batch = uniques.ACTIVE_SCENE.world_batch
        # )

        # fish: WaterFishNode = WaterFishNode(
        #     x = SETTINGS[Keys.VIEW_WIDTH] / 2,
        #     y = SETTINGS[Keys.VIEW_HEIGHT] / 2,
        #     batch = uniques.ACTIVE_SCENE.world_batch
        # )

        # Add children to the active scene.
        # uniques.ACTIVE_SCENE.add_child(fish)

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
        # Benchmark measures update time.
        # Compute collisions through collision manager.
        controllers.COLLISION_CONTROLLER.update(dt = dt)

        # InputController makes sure every input is handled correctly.
        with controllers.INPUT_CONTROLLER:
            if uniques.ACTIVE_SCENE is not None:
                uniques.ACTIVE_SCENE.update(dt = dt)

    def run(self) -> None:
        pyglet.clock.schedule_interval(self.update, 1.0 / (2.0 * SETTINGS[Keys.TARGET_FPS]))
        pyglet.app.run(interval =  1.0 / SETTINGS[Keys.TARGET_FPS])

FishGame().run()