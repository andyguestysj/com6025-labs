import moderngl
import moderngl_window as mglw
import numpy as np
import glm


def load_shader(path):
  with open(path, 'r') as f:
    return f.read()


class ColouredCube(mglw.WindowConfig):
  gl_version = (3, 3)
  title = "COM6025M — Coloured Cube"
  window_size = (800, 600)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

    vertices = np.array([
      -0.5, -0.5,  0.5,  1.0, 0.0, 0.0,
      0.5, -0.5,  0.5,  0.0, 1.0, 0.0,
      0.5,  0.5,  0.5,  0.0, 0.0, 1.0,
      -0.5,  0.5,  0.5,  1.0, 1.0, 0.0,
      -0.5, -0.5, -0.5,  0.0, 1.0, 1.0,
      0.5, -0.5, -0.5,  1.0, 0.0, 1.0,
      0.5,  0.5, -0.5,  1.0, 1.0, 1.0,
      -0.5,  0.5, -0.5,  0.5, 0.5, 0.5,
    ], dtype='f4')

    indices = np.array([
      0, 1, 2,  2, 3, 0,
      1, 5, 6,  6, 2, 1,
      5, 4, 7,  7, 6, 5,
      4, 0, 3,  3, 7, 4,
      3, 2, 6,  6, 7, 3,
      4, 5, 1,  1, 0, 4,
    ], dtype='i4')

    vbo = self.ctx.buffer(vertices)
    ibo = self.ctx.buffer(indices)

    self.prog = self.ctx.program(
      vertex_shader=load_shader('week02/shaders/cube.vert'),
      fragment_shader=load_shader('week02/shaders/cube.frag'),
    )

    self.vao = self.ctx.vertex_array(
      self.prog,
      [(vbo, '3f 3f', 'in_position', 'in_color')],
      index_buffer=ibo,
      index_element_size=4,
    )

  def on_render(self, time, frame_time):
    self.ctx.clear(0.1, 0.1, 0.1)
    self.ctx.clear(depth=True)
    model = glm.rotate(glm.mat4(), glm.radians(30), glm.vec3(1, 0, 0))
    model = glm.rotate(model, time, glm.vec3(0, 1, 0))
    self.prog['m_model'].write(model)
    self.vao.render()



if __name__ == '__main__':
  mglw.run_window_config(ColouredCube)