import math

import moderngl
import moderngl_window as mglw
import numpy as np
import glm
from PIL import Image

def load_shader(path):
  with open(path, 'r') as f:
    return f.read()


OBJECTS = [
  {'position': glm.vec3(-1.5, 0.0, 0.0), 'axis': glm.vec3(0, 1, 0), 'speed': 1.0, 'scale': 0.5},
  {'position': glm.vec3( 0.0, 0.0, -1.5), 'axis': glm.vec3(1, 0, 0), 'speed': 0.6, 'scale': 0.5},
  {'position': glm.vec3( 1.5, 0.0, 0.0), 'axis': glm.vec3(0, 0, 1), 'speed': 1.4, 'scale': 0.5},
]


class TextureDemo(mglw.WindowConfig):
  gl_version = (3, 3)
  title = "COM6025M — Textures"
  window_size = (800, 600)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
    
    img = Image.open('week05/textures/diffuse.png').convert('RGB')
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    self.tex_diffuse = self.ctx.texture(img.size, 3, img.tobytes())
    self.tex_diffuse.filter = (moderngl.LINEAR, moderngl.LINEAR)
    self.tex_diffuse.build_mipmaps()
    self.tex_diffuse.repeat_x = True
    self.tex_diffuse.repeat_y = True
    
    img2 = Image.open('week05/textures/detail.png').convert('RGB')
    img2 = img2.transpose(Image.FLIP_TOP_BOTTOM)
    self.tex_detail = self.ctx.texture(img2.size, 3, img2.tobytes())
    self.tex_detail.filter = (moderngl.LINEAR, moderngl.LINEAR)
    self.tex_detail.repeat_x = True
    self.tex_detail.repeat_y = True
    
    img3 = Image.open('week05/textures/normal.png').convert('RGB')
    img3 = img3.transpose(Image.FLIP_TOP_BOTTOM)
    self.tex_normal = self.ctx.texture(img3.size, 3, img3.tobytes())
    self.tex_normal.filter = (moderngl.LINEAR, moderngl.LINEAR)

    FACES = [
      ([(-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)], (1, 1, 1)),  # front
      ([(0.5, -0.5, 0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5)], (1, 1, 1)),  # right
      ([(0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5)], (1, 1, 1)),  # back
      ([(-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5)], (1, 1, 1)),  # left
      ([(-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5)], (1, 1, 1)),  # top
      ([(-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5)], (1, 1, 1)),  # bottom
    ]
    UVS = [(0, 0), (1, 0), (1, 1), (0, 1)]

    vertex_data = []
    index_data = []
    for face_i, (positions, color) in enumerate(FACES):
      base = face_i * 4
      for pos, uv in zip(positions, UVS):
        vertex_data.extend(pos)
        vertex_data.extend(color)
        vertex_data.extend(uv)
      index_data.extend([base, base + 1, base + 2, base + 2, base + 3, base])

    vertices = np.array(vertex_data, dtype='f4')
    indices = np.array(index_data, dtype='i4')

    vbo = self.ctx.buffer(vertices.tobytes())
    ibo = self.ctx.buffer(indices.tobytes())

    
    self.prog = self.ctx.program(
      vertex_shader=load_shader('week05/shaders/cube.vert'),
      fragment_shader=load_shader('week05/shaders/cube.frag'),
    )

    self.vao = self.ctx.vertex_array(
      self.prog,
      [(vbo, '3f 3f 2f', 'in_position', 'in_color', 'in_uv')],  
      index_buffer=ibo,                              
      index_element_size=4,                          
    )
    
    width, height = self.window_size
    aspect_ratio = width / height
    self.proj = glm.perspective(glm.radians(60.0), aspect_ratio, 0.1, 100.0)
    self.prog['m_proj'].write(self.proj)
        
  ###################################################
  # on_render is called every frame to draw the scene
  ###################################################
        
  def on_render(self, time, frame_time):
    self.ctx.clear(0.1, 0.1, 0.1)
    self.ctx.clear(depth=True)
    
    self.tex_diffuse.use(location=0)
    self.prog['tex0'].value = 0
    self.tex_detail.use(location=1)
    self.prog['tex1'].value = 1
    #self.tex_normal.use(location=0)
    #self.prog['tex_normal'].value = 0
    
    radius = 4.0
    eye = glm.vec3(radius * math.sin(time), 1.5, radius * math.cos(time))
    target = glm.vec3(0.0, 0.0, 0.0)
    up = glm.vec3(0.0, 1.0, 0.0)
    self.view = glm.lookAt(eye, target, up) 
    self.prog['m_view'].write(self.view)

    for obj in OBJECTS:
      model = glm.translate(glm.mat4(), obj['position'])
      model = glm.rotate(model, time * obj['speed'], obj['axis'])
      model = glm.scale(model, glm.vec3(obj['scale']))
      self.prog['m_model'].write(model)
      self.vao.render()


if __name__ == '__main__':
  mglw.run_window_config(TextureDemo)