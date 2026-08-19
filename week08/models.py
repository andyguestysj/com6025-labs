import moderngl
import moderngl_window as mglw
import numpy as np
import glm
import math
from PIL import Image


def load_shader(path):
  with open(path, 'r') as f:
    return f.read()

def load_obj(path):
  """
  A minimal Wavefront OBJ loader. Handles v / vt / vn / f lines only, and
  assumes every face is already a triangle (three v/vt/vn refs per f line —
  true for this week's generated gem, but not guaranteed for an arbitrary
  export; a real loader would fan-triangulate any face with more than three).

  Produces a flat, non-indexed vertex buffer: every face gets three fresh
  vertices, the same "one vertex, one set of attributes" approach used for
  the cube's UVs since Week 5 — no de-duplication, no index buffer.
  """
  positions = []
  uvs = []
  normals = []
  vertex_data = []

  with open(path, 'r') as f:
    for line in f:
      line = line.strip()
      if line.startswith('v '):
        positions.append(tuple(float(x) for x in line.split()[1:4]))
      elif line.startswith('vt '):
        uvs.append(tuple(float(x) for x in line.split()[1:3]))
      elif line.startswith('vn '):
        normals.append(tuple(float(x) for x in line.split()[1:4]))
      elif line.startswith('f '):
        for ref in line.split()[1:4]:
          vi, ti, ni = (int(i) for i in ref.split('/'))
          vertex_data.extend(positions[vi - 1])
          vertex_data.extend((1.0, 1.0, 1.0))  # flat white — OBJ has no per-vertex colour
          vertex_data.extend(normals[ni - 1])
          vertex_data.extend(uvs[ti - 1])

  return np.array(vertex_data, dtype='f4')

MODEL_INSTANCES = [
  {'position': glm.vec3(-1.2, 0.0, 0.0), 'axis': glm.vec3(0, 1, 0), 'speed': 0.8},
  {'position': glm.vec3( 1.2, 0.0, 0.0), 'axis': glm.vec3(0, 1, 0), 'speed': -0.6},
]

POINT_LIGHTS = [
  {'position': glm.vec3(-2.0, 1.5, 1.5), 'color': glm.vec3(1.0, 0.3, 0.3), 'constant': 1.0, 'linear': 0.09, 'quadratic': 0.032},
  {'position': glm.vec3( 2.0, 1.0, -1.0), 'color': glm.vec3(0.3, 0.5, 1.0), 'constant': 1.0, 'linear': 0.09, 'quadratic': 0.032},
]




class ModelsDemo(mglw.WindowConfig):
  gl_version = (3, 3)
  title = "COM6025M — Models"
  window_size = (800, 600)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

    self.prog = self.ctx.program(
      vertex_shader=load_shader('week08/shaders/model.vert'),
      fragment_shader=load_shader('week08/shaders/model.frag'),
    )

    vertices = load_obj('week08/models/gem.obj')
    vbo = self.ctx.buffer(vertices.tobytes())

    self.vao = self.ctx.vertex_array(
      self.prog,
      [(vbo, '3f 3f 3f 2f', 'in_position', 'in_color', 'in_normal', 'in_uv')],
    )

    img = Image.open('week08/textures/gem.png').convert('RGB')
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    self.tex_diffuse = self.ctx.texture(img.size, 3, img.tobytes())
    self.tex_diffuse.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
    self.tex_diffuse.repeat_x = True
    self.tex_diffuse.repeat_y = True
    self.tex_diffuse.build_mipmaps()



    eye = glm.vec3(0.0, 1.5, 4.0)
    target = glm.vec3(0.0, 0.0, 0.0)
    up = glm.vec3(0.0, 1.0, 0.0)
    self.view = glm.lookAt(eye, target, up)
    self.prog['m_view'].write(self.view)

    width, height = self.window_size
    aspect_ratio = width / height
    self.proj = glm.perspective(glm.radians(60.0), aspect_ratio, 0.1, 100.0)
    self.prog['m_proj'].write(self.proj)
    
    self.prog['view_pos'].value = tuple(eye)
    self.prog['material.shininess'].value = 32.0

    for i, light in enumerate(POINT_LIGHTS):
      self.prog[f'point_lights[{i}].position'].value = tuple(light['position'])
      self.prog[f'point_lights[{i}].color'].value = tuple(light['color'])
      self.prog[f'point_lights[{i}].constant'].value = light['constant']
      self.prog[f'point_lights[{i}].linear'].value = light['linear']
      self.prog[f'point_lights[{i}].quadratic'].value = light['quadratic']

    spot_dir = glm.normalize(target - eye)
    self.prog['spot_light.position'].value = tuple(eye)
    self.prog['spot_light.direction'].value = tuple(spot_dir)
    self.prog['spot_light.color'].value = (1.0, 1.0, 1.0)
    self.prog['spot_light.cutoff'].value = math.cos(math.radians(25.))
    self.prog['spot_light.outer_cutoff'].value = math.cos(math.radians(17.5))
    self.prog['spot_light.constant'].value = 1.0
    self.prog['spot_light.linear'].value = 0.09
    self.prog['spot_light.quadratic'].value = 0.032
    
    
  ###############################################
  # on_render is called every frame to draw the scene
  ###############################################

  def on_render(self, time, frame_time):
    self.ctx.clear(0.1, 0.1, 0.1)
    self.ctx.clear(depth=True)

    self.tex_diffuse.use(location=0)
    self.prog['tex0'].value = 0    
    
    base_dir = glm.vec3(-0.3, -1.0, -0.3)
    rot = glm.rotate(glm.mat4(), time * 0.5, glm.vec3(0, 1, 0))
    animated_dir = glm.normalize(glm.vec3(rot * glm.vec4(base_dir, 0.0)))    

    for obj in MODEL_INSTANCES:
      model = glm.translate(glm.mat4(), obj['position'])
      model = glm.rotate(model, time * obj['speed'], obj['axis'])      
      self.prog['m_model'].write(model)
      self.vao.render()


if __name__ == '__main__':
  mglw.run_window_config(ModelsDemo)