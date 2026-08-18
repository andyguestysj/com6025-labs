import math

import moderngl
import moderngl_window as mglw
import numpy as np
import glm


def load_shader(path):
  with open(path, 'r') as f:
    return f.read()


OBJECTS = [
  {'position': glm.vec3(-0.6, 0.0, 0.0), 'axis': glm.vec3(0, 1, 0), 'speed': 1.0, 'scale': 0.35},
  {'position': glm.vec3( 0.0, 0.0, 0.0), 'axis': glm.vec3(1, 0, 0), 'speed': 0.6, 'scale': 0.5},
  {'position': glm.vec3( 0.6, 0.0, 0.0), 'axis': glm.vec3(0, 0, 1), 'speed': 1.4, 'scale': 0.35},
]


class TransformDemo(mglw.WindowConfig):
  gl_version = (3, 3)
  title = "COM6025M — Transforms"
  window_size = (800, 600)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
    self.view_tilt = glm.rotate(glm.mat4(), glm.radians(30), glm.vec3(1, 0, 0))

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
      vertex_shader=load_shader('week03/shaders/cube.vert'),
      fragment_shader=load_shader('week03/shaders/cube.frag'),
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

    for obj in OBJECTS:
      model = glm.translate(self.view_tilt, obj['position'])
      model = glm.rotate(model, time * obj['speed'], obj['axis'])
      model = glm.scale(model, glm.vec3(obj['scale']))
      self.prog['m_model'].write(model)
      self.vao.render()


if __name__ == '__main__':
  mglw.run_window_config(TransformDemo)