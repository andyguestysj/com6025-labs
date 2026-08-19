import moderngl
import moderngl_window as mglw
import numpy as np
import glm
from PIL import Image


def load_shader(path):
  with open(path, 'r') as f:
    return f.read()


SHADOW_SIZE = 1024

OBJECTS = [
  # y = -0.2 rests the cube on the floor: floor top is y = -0.5, and a unit
  # cube at scale 0.6 has half-height 0.3, so -0.5 + 0.3 = -0.2.
  {'position': glm.vec3(-1.0, -0.2, 0.0), 'axis': glm.vec3(0, 1, 0), 'speed': 0.6, 'scale': 0.6},
  {'position': glm.vec3( 1.0, -0.2, -0.5), 'axis': glm.vec3(0, 1, 0), 'speed': -0.4, 'scale': 0.6},
]


def build_cube():
  FACES = [
    ([(-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)], (1, 1, 1), (0, 0, 1)),    # front
    ([(0.5, -0.5, 0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5)], (1, 1, 1), (1, 0, 0)),    # right
    ([(0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5)], (1, 1, 1), (0, 0, -1)),  # back
    ([(-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5)], (1, 1, 1), (-1, 0, 0)),  # left
    ([(-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5)], (1, 1, 1), (0, 1, 0)),    # top
    ([(-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5)], (1, 1, 1), (0, -1, 0)),  # bottom
  ]
  UVS = [(0, 0), (1, 0), (1, 1), (0, 1)]

  vertex_data = []
  index_data = []
  for face_i, (positions, color, normal) in enumerate(FACES):
    base = face_i * 4
    for pos, uv in zip(positions, UVS):
      vertex_data.extend(pos)
      vertex_data.extend(color)
      vertex_data.extend(normal)
      vertex_data.extend(uv)
    index_data.extend([base, base + 1, base + 2, base + 2, base + 3, base])

  return np.array(vertex_data, dtype='f4'), np.array(index_data, dtype='i4')


def build_floor():
  half = 3.0
  y = -0.5
  # Wound so the normal (0, 1, 0) faces up, toward the camera — get this
  # backwards and back-face culling will make the floor invisible.
  positions = [(-half, y, -half), (-half, y, half), (half, y, half), (half, y, -half)]
  uvs = [(0, 0), (0, 4), (4, 4), (4, 0)]
  normal = (0, 1, 0)
  color = (1, 1, 1)

  vertex_data = []
  for pos, uv in zip(positions, uvs):
    vertex_data.extend(pos)
    vertex_data.extend(color)
    vertex_data.extend(normal)
    vertex_data.extend(uv)
  index_data = [0, 1, 2, 2, 3, 0]

  return np.array(vertex_data, dtype='f4'), np.array(index_data, dtype='i4')

class ShadowsDemo(mglw.WindowConfig):
  gl_version = (3, 3)
  title = "COM6025M — Shadows"
  window_size = (800, 600)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

    self.depth_prog = self.ctx.program(
      vertex_shader=load_shader('week09/shaders/depth.vert'),
      fragment_shader=load_shader('week09/shaders/depth.frag'),
    )
    self.scene_prog = self.ctx.program(
      vertex_shader=load_shader('week09/shaders/scene.vert'),
      fragment_shader=load_shader('week09/shaders/scene.frag'),
    )

    cube_vertices, cube_indices = build_cube()
    self.cube_vbo = self.ctx.buffer(cube_vertices.tobytes())
    self.cube_ibo = self.ctx.buffer(cube_indices.tobytes())

    floor_vertices, floor_indices = build_floor()
    self.floor_vbo = self.ctx.buffer(floor_vertices.tobytes())
    self.floor_ibo = self.ctx.buffer(floor_indices.tobytes())

    self.cube_vao_scene = self.ctx.vertex_array(
      self.scene_prog,
      [(self.cube_vbo, '3f 3f 3f 2f', 'in_position', 'in_color', 'in_normal', 'in_uv')],
      index_buffer=self.cube_ibo, index_element_size=4,
    )
    self.cube_vao_depth = self.ctx.vertex_array(
      self.depth_prog,
      [(self.cube_vbo, '3f 32x', 'in_position')],
      index_buffer=self.cube_ibo, index_element_size=4,
    )
    self.floor_vao_scene = self.ctx.vertex_array(
      self.scene_prog,
      [(self.floor_vbo, '3f 3f 3f 2f', 'in_position', 'in_color', 'in_normal', 'in_uv')],
      index_buffer=self.floor_ibo, index_element_size=4,
    )
    self.floor_vao_depth = self.ctx.vertex_array(
      self.depth_prog,
      [(self.floor_vbo, '3f 32x', 'in_position')],
      index_buffer=self.floor_ibo, index_element_size=4,
    )
    
    img = Image.open('week09/textures/diffuse.png').convert('RGB')
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    self.tex_diffuse = self.ctx.texture(img.size, 3, img.tobytes())
    self.tex_diffuse.filter = (moderngl.LINEAR, moderngl.LINEAR)
    self.tex_diffuse.repeat_x = True
    self.tex_diffuse.repeat_y = True
    
    self.shadow_map = self.ctx.depth_texture((SHADOW_SIZE, SHADOW_SIZE))
    self.shadow_map.compare_func = ''
    self.shadow_map.repeat_x = False
    self.shadow_map.repeat_y = False
    self.shadow_fbo = self.ctx.framebuffer(depth_attachment=self.shadow_map)
    
    eye = glm.vec3(0.0, 2.0, 4.5)
    target = glm.vec3(0.0, 0.0, 0.0)
    up = glm.vec3(0.0, 1.0, 0.0)
    self.view = glm.lookAt(eye, target, up)
    self.scene_prog['m_view'].write(self.view)

    width, height = self.window_size
    aspect_ratio = width / height
    self.proj = glm.perspective(glm.radians(60.0), aspect_ratio, 0.1, 100.0)
    self.scene_prog['m_proj'].write(self.proj)

    self.light_dir = glm.normalize(glm.vec3(-0.4, -1.0, -0.3))
    light_pos = target - self.light_dir * 8.0
    light_view = glm.lookAt(light_pos, target, glm.vec3(0.0, 1.0, 0.0))
    light_proj = glm.ortho(-4.0, 4.0, -4.0, 4.0, 1.0, 20.0)
    self.light_space_matrix = light_proj * light_view

    self.scene_prog['view_pos'].value = tuple(eye)
    self.scene_prog['light_dir'].value = tuple(self.light_dir)
    self.scene_prog['light_color'].value = (1.0, 1.0, 1.0)
    self.scene_prog['ambient_strength'].value = 0.2
    self.scene_prog['shininess'].value = 32.0
    
  def draw_scene(self, prog, time):
    for obj in OBJECTS:
      model = glm.translate(glm.mat4(), obj['position'])
      model = glm.rotate(model, time * obj['speed'], obj['axis'])
      model = glm.scale(model, glm.vec3(obj['scale']))
      prog['m_model'].write(model)
      if prog is self.depth_prog:
        self.cube_vao_depth.render()
      else:
        self.cube_vao_scene.render()

    floor_model = glm.mat4()
    prog['m_model'].write(floor_model)
    if prog is self.depth_prog:
      self.floor_vao_depth.render()
    else:
      self.floor_vao_scene.render()

  def on_render(self, time, frame_time):
    # Pass 1 — render depth from the light's point of view.
    self.depth_prog['light_space_matrix'].write(self.light_space_matrix)
    self.shadow_fbo.use()
    self.shadow_fbo.clear(depth=1.0)
    self.ctx.enable_only(moderngl.DEPTH_TEST)
    self.draw_scene(self.depth_prog, time)

    # Pass 2 — render the scene normally, sampling the shadow map.
    self.wnd.use()
    self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
    self.ctx.clear(0.05, 0.05, 0.08)

    self.tex_diffuse.use(location=0)
    self.scene_prog['tex0'].value = 0
    self.shadow_map.use(location=1)
    self.scene_prog['shadow_map'].value = 1
    self.scene_prog['light_space_matrix'].write(self.light_space_matrix)

    self.draw_scene(self.scene_prog, time)
    
if __name__ == '__main__':
  mglw.run_window_config(ShadowsDemo)