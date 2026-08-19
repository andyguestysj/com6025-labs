import moderngl
import moderngl_window as mglw
import numpy as np
import glm
from PIL import Image


def load_shader(path):
  with open(path, 'r') as f:
    return f.read()


FACES = [
  ([(-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)], (0, 0, 1), (1, 0, 0)),    # front
  ([(0.5, -0.5, 0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5)], (1, 0, 0), (0, 0, -1)),   # right
  ([(0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5)], (0, 0, -1), (-1, 0, 0)),  # back
  ([(-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5)], (-1, 0, 0), (0, 0, 1)),  # left
  ([(-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5)], (0, 1, 0), (1, 0, 0)),    # top
  ([(-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5)], (0, -1, 0), (1, 0, 0)),  # bottom
]
UVS = [(0, 0), (1, 0), (1, 1), (0, 1)]


def build_pbr_cube():
  vertex_data = []
  index_data = []
  for face_i, (positions, normal, tangent) in enumerate(FACES):
    base = face_i * 4
    for pos, uv in zip(positions, UVS):
      vertex_data.extend(pos)
      vertex_data.extend(normal)
      vertex_data.extend(tangent)
      vertex_data.extend(uv)
    index_data.extend([base, base + 1, base + 2, base + 2, base + 3, base])
  return np.array(vertex_data, dtype='f4'), np.array(index_data, dtype='i4')


def build_phong_cube():
  vertex_data = []
  index_data = []
  for face_i, (positions, normal, _tangent) in enumerate(FACES):
    base = face_i * 4
    for pos, uv in zip(positions, UVS):
      vertex_data.extend(pos)
      vertex_data.extend((1, 1, 1))
      vertex_data.extend(normal)
      vertex_data.extend(uv)
    index_data.extend([base, base + 1, base + 2, base + 2, base + 3, base])
  return np.array(vertex_data, dtype='f4'), np.array(index_data, dtype='i4')

class PBRDemo(mglw.WindowConfig):
  gl_version = (3, 3)
  title = "COM6025M — Physically Based Rendering"
  window_size = (800, 600)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

    self.pbr_prog = self.ctx.program(
      vertex_shader=load_shader('week10/shaders/pbr.vert'),
      fragment_shader=load_shader('week10/shaders/pbr.frag'),
    )
    self.phong_prog = self.ctx.program(
      vertex_shader=load_shader('week10/shaders/phong.vert'),
      fragment_shader=load_shader('week10/shaders/phong.frag'),
    )

    pbr_vertices, pbr_indices = build_pbr_cube()
    pbr_vbo = self.ctx.buffer(pbr_vertices.tobytes())
    pbr_ibo = self.ctx.buffer(pbr_indices.tobytes())
    self.pbr_vao = self.ctx.vertex_array(
      self.pbr_prog,
      [(pbr_vbo, '3f 3f 3f 2f', 'in_position', 'in_normal', 'in_tangent', 'in_uv')],
      index_buffer=pbr_ibo, index_element_size=4,
    )

    phong_vertices, phong_indices = build_phong_cube()
    phong_vbo = self.ctx.buffer(phong_vertices.tobytes())
    phong_ibo = self.ctx.buffer(phong_indices.tobytes())
    self.phong_vao = self.ctx.vertex_array(
      self.phong_prog,
      [(phong_vbo, '3f 3f 3f 2f', 'in_position', 'in_color', 'in_normal', 'in_uv')],
      index_buffer=phong_ibo, index_element_size=4,
    )

    def load_tex(path):
      img = Image.open(path).convert('RGB')
      img = img.transpose(Image.FLIP_TOP_BOTTOM)
      tex = self.ctx.texture(img.size, 3, img.tobytes())
      tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
      return tex

    self.tex_albedo = load_tex('week10/textures/albedo.png')
    self.tex_normal = load_tex('week10/textures/normal.png')
    self.tex_roughness = load_tex('week10/textures/roughness.png')
    self.tex_metallic = load_tex('week10/textures/metallic.png')
    self.tex_ao = load_tex('week10/textures/ao.png')
    self.tex_diffuse = load_tex('week10/textures/diffuse.png')

    eye = glm.vec3(0.0, 1.5, 4.0)
    target = glm.vec3(0.0, 0.0, 0.0)
    up = glm.vec3(0.0, 1.0, 0.0)
    view = glm.lookAt(eye, target, up)

    width, height = self.window_size
    aspect_ratio = width / height
    proj = glm.perspective(glm.radians(60.0), aspect_ratio, 0.1, 100.0)

    for prog in (self.pbr_prog, self.phong_prog):
      prog['m_view'].write(view)
      prog['m_proj'].write(proj)

    light_pos = glm.vec3(2.0, 2.0, 3.0)

    self.pbr_prog['view_pos'].value = tuple(eye)
    self.pbr_prog['light_pos'].value = tuple(light_pos)
    self.pbr_prog['light_color'].value = (30.0, 30.0, 30.0)
    self.pbr_prog['tex_albedo'].value = 0
    self.pbr_prog['tex_normal'].value = 1
    self.pbr_prog['tex_roughness'].value = 2
    self.pbr_prog['tex_metallic'].value = 3
    self.pbr_prog['tex_ao'].value = 4

    light_dir = glm.normalize(-light_pos)
    self.phong_prog['view_pos'].value = tuple(eye)
    self.phong_prog['light_dir'].value = tuple(light_dir)
    self.phong_prog['light_color'].value = (1.0, 1.0, 1.0)
    self.phong_prog['ambient_strength'].value = 0.15
    self.phong_prog['shininess'].value = 32.0
    self.phong_prog['tex0'].value = 5

###############################################
# on_render is called every frame to draw the scene
###############################################

  def on_render(self, time, frame_time):
    self.ctx.clear(0.02, 0.02, 0.03)
    self.ctx.clear(depth=True)

    self.tex_albedo.use(location=0)
    self.tex_normal.use(location=1)
    self.tex_roughness.use(location=2)
    self.tex_metallic.use(location=3)
    self.tex_ao.use(location=4)

    model = glm.translate(glm.mat4(), glm.vec3(-1.1, 0.0, 0.0))
    model = glm.rotate(model, time * 0.4, glm.vec3(0, 1, 0))
    self.pbr_prog['m_model'].write(model)
    self.pbr_vao.render()

    self.tex_diffuse.use(location=5)

    model = glm.translate(glm.mat4(), glm.vec3(1.1, 0.0, 0.0))
    model = glm.rotate(model, time * 0.4, glm.vec3(0, 1, 0))
    self.phong_prog['m_model'].write(model)
    self.phong_vao.render()


if __name__ == '__main__':
  mglw.run_window_config(PBRDemo)