from io import TextIOWrapper
import pyglet


def load_shader(
    vert_file_path: str | None = None,
    frag_file_path: str | None = None
) -> pyglet.graphics.shader.ShaderProgram:
    """
    Creates and return a shader program by reading it from source.
    If source file paths are not provided, the default pyglet sources are used.
    """

    vert_src: str = pyglet.sprite.vertex_source
    frag_src: str = pyglet.sprite.fragment_source

    if vert_file_path is not None:
        vert_file: TextIOWrapper = open(vert_file_path)
        vert_src: str = vert_file.read()
        vert_file.close()

    if frag_file_path is not None:
        frag_file: TextIOWrapper = open(frag_file_path)
        frag_src: str = frag_file.read()
        frag_file.close()

    vert_shader: pyglet.graphics.shader.Shader = pyglet.graphics.shader.Shader(vert_src, "vertex")
    frag_shader: pyglet.graphics.shader.Shader = pyglet.graphics.shader.Shader(frag_src, "fragment")

    return pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)