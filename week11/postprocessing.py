import moderngl
import moderngl_window as mglw
import numpy as np
import glm
from PIL import Image


def load_shader(path):
  with open(path, 'r') as f:
    return f.read()


OBJECTS = [
  {'position': glm.vec3(-1.5, 0.0,  0.0), 'axis': glm.vec3(0, 1, 0), 'speed': 1.0, 'scale': 0.5},
  {'position': glm.vec3( 0.0, 0.0, -1.5), 'axis': glm.vec3(1, 0, 0), 'speed': 0.6, 'scale': 0.5},
  {'position': glm.vec3( 1.5, 0.0,  0.0), 'axis': glm.vec3(0, 0, 1), 'speed': 1.4, 'scale': 0.5},
]

LAMP = {'position': glm.vec3(0.0, 1.3, 0.0), 'scale': 0.25}
BLUR_PASSES = 4


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


def build_fullscreen_quad():
  data = np.array([
    -1, -1,  0, 0,
     1, -1,  1, 0,
     1,  1,  1, 1,
    -1, -1,  0, 0,
     1,  1,  1, 1,
    -1,  1,  0, 1,
  ], dtype='f4')
  return data

class PostProcessingDemo(mglw.WindowConfig):
  gl_version = (3, 3)
  title = "COM6025M — Post-Processing"
  window_size = (800, 600)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

    self.cube_prog = self.ctx.program(
      vertex_shader=load_shader('week11/shaders/cube.vert'),
      fragment_shader=load_shader('week11/shaders/cube.frag'),
    )
    self.emissive_prog = self.ctx.program(
      vertex_shader=load_shader('week11/shaders/emissive.vert'),
      fragment_shader=load_shader('week11/shaders/emissive.frag'),
    )
    self.greyscale_prog = self.ctx.program(
      vertex_shader=load_shader('week11/shaders/post.vert'),
      fragment_shader=load_shader('week11/shaders/greyscale.frag'),
    )
    self.edge_prog = self.ctx.program(
      vertex_shader=load_shader('week11/shaders/post.vert'),
      fragment_shader=load_shader('week11/shaders/edge.frag'),
    )
    self.brightpass_prog = self.ctx.program(
      vertex_shader=load_shader('week11/shaders/post.vert'),
      fragment_shader=load_shader('week11/shaders/brightpass.frag'),
    )
    self.blur_prog = self.ctx.program(
      vertex_shader=load_shader('week11/shaders/post.vert'),
      fragment_shader=load_shader('week11/shaders/blur.frag'),
    )
    self.composite_prog = self.ctx.program(
      vertex_shader=load_shader('week11/shaders/post.vert'),
      fragment_shader=load_shader('week11/shaders/composite.frag'),
    )

    cube_vertices, cube_indices = build_cube()
    cube_vbo = self.ctx.buffer(cube_vertices.tobytes())
    cube_ibo = self.ctx.buffer(cube_indices.tobytes())
    self.cube_vao = self.ctx.vertex_array(
      self.cube_prog,
      [(cube_vbo, '3f 3f 3f 2f', 'in_position', 'in_color', 'in_normal', 'in_uv')],
      index_buffer=cube_ibo, index_element_size=4,
    )
    self.lamp_vao = self.ctx.vertex_array(
      self.emissive_prog,
      [(cube_vbo, '3f 32x', 'in_position')],
      index_buffer=cube_ibo, index_element_size=4,
    )

    quad_data = build_fullscreen_quad()
    quad_vbo = self.ctx.buffer(quad_data.tobytes())

    def make_quad_vao(prog):
      return self.ctx.vertex_array(prog, [(quad_vbo, '2f 2f', 'in_position', 'in_uv')])

    self.quad_greyscale = make_quad_vao(self.greyscale_prog)
    self.quad_edge = make_quad_vao(self.edge_prog)
    self.quad_brightpass = make_quad_vao(self.brightpass_prog)
    self.quad_blur = make_quad_vao(self.blur_prog)
    self.quad_composite = make_quad_vao(self.composite_prog)
    
    img = Image.open('week11/textures/diffuse.png').convert('RGB')
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    self.tex_diffuse = self.ctx.texture(img.size, 3, img.tobytes())
    self.tex_diffuse.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
    self.tex_diffuse.repeat_x = True
    self.tex_diffuse.repeat_y = True
    self.tex_diffuse.build_mipmaps()
    
    width, height = self.window_size

    self.scene_color = self.ctx.texture((width, height), 3, dtype='f2')
    self.scene_depth = self.ctx.depth_renderbuffer((width, height))
    self.scene_fbo = self.ctx.framebuffer(color_attachments=[self.scene_color], depth_attachment=self.scene_depth)

    self.bright_color = self.ctx.texture((width, height), 3, dtype='f2')
    self.bright_fbo = self.ctx.framebuffer(color_attachments=[self.bright_color])

    self.blur_color_a = self.ctx.texture((width, height), 3, dtype='f2')
    self.blur_fbo_a = self.ctx.framebuffer(color_attachments=[self.blur_color_a])
    self.blur_color_b = self.ctx.texture((width, height), 3, dtype='f2')
    self.blur_fbo_b = self.ctx.framebuffer(color_attachments=[self.blur_color_b])
    
    eye = glm.vec3(0.0, 1.5, 4.0)
    target = glm.vec3(0.0, 0.0, 0.0)
    up = glm.vec3(0.0, 1.0, 0.0)
    view = glm.lookAt(eye, target, up)
    aspect_ratio = width / height
    proj = glm.perspective(glm.radians(60.0), aspect_ratio, 0.1, 100.0)

    self.cube_prog['m_view'].write(view)
    self.cube_prog['m_proj'].write(proj)
    self.cube_prog['view_pos'].value = tuple(eye)
    self.cube_prog['light_dir'].value = tuple(glm.normalize(glm.vec3(-0.4, -1.0, -0.3)))
    self.cube_prog['light_color'].value = (1.0, 1.0, 1.0)
    self.cube_prog['ambient_strength'].value = 0.15
    self.cube_prog['shininess'].value = 32.0

    self.emissive_prog['m_view'].write(view)
    self.emissive_prog['m_proj'].write(proj)
    self.emissive_prog['emissive_color'].value = (4.0, 3.6, 1.2)  # deliberately > 1.0

    self.texel_size = (1.0 / width, 1.0 / height)
    self.mode = 'bloom'  # 'bloom', 'greyscale', or 'edge'
    self.bloom_intensity = 4.0  # multiplies the blurred bloom before it's added to the scene
    
################################
# on_render is called every frame to draw the scene
################################

  def render_scene(self, time):
    self.tex_diffuse.use(location=0)
    self.cube_prog['tex0'].value = 0
    for obj in OBJECTS:
      model = glm.translate(glm.mat4(), obj['position'])
      model = glm.rotate(model, time * obj['speed'], obj['axis'])
      model = glm.scale(model, glm.vec3(obj['scale']))
      self.cube_prog['m_model'].write(model)
      self.cube_vao.render()

    lamp_model = glm.translate(glm.mat4(), LAMP['position'])
    lamp_model = glm.scale(lamp_model, glm.vec3(LAMP['scale']))
    self.emissive_prog['m_model'].write(lamp_model)
    self.lamp_vao.render()

  def on_render(self, time, frame_time):
    self.scene_fbo.use()
    self.ctx.clear(0.05, 0.05, 0.08)
    self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
    self.render_scene(time)

    if self.mode == 'bloom':
      self.ctx.disable(moderngl.DEPTH_TEST)
      self.bright_fbo.use()
      self.scene_color.use(location=0)
      self.brightpass_prog['scene_tex'].value = 0
      self.brightpass_prog['threshold'].value = 1.0
      self.quad_brightpass.render()

      src = self.bright_color
      for i in range(BLUR_PASSES):
        self.blur_fbo_a.use()
        src.use(location=0)
        self.blur_prog['scene_tex'].value = 0
        self.blur_prog['texel_size'].value = self.texel_size
        self.blur_prog['direction'].value = (1.0, 0.0)
        self.quad_blur.render()

        self.blur_fbo_b.use()
        self.blur_color_a.use(location=0)
        self.blur_prog['scene_tex'].value = 0
        self.blur_prog['direction'].value = (0.0, 1.0)
        self.quad_blur.render()

        src = self.blur_color_b

      self.wnd.use()
      self.scene_color.use(location=0)
      self.blur_color_b.use(location=1)
      self.composite_prog['scene_tex'].value = 0
      self.composite_prog['bloom_tex'].value = 1
      self.composite_prog['bloom_intensity'].value = self.bloom_intensity
      self.quad_composite.render()

    elif self.mode == 'greyscale':
      self.wnd.use()
      self.ctx.disable(moderngl.DEPTH_TEST)
      self.scene_color.use(location=0)
      self.greyscale_prog['scene_tex'].value = 0
      self.quad_greyscale.render()

    elif self.mode == 'edge':
      self.wnd.use()
      self.ctx.disable(moderngl.DEPTH_TEST)
      self.scene_color.use(location=0)
      self.edge_prog['scene_tex'].value = 0
      self.edge_prog['texel_size'].value = self.texel_size
      self.quad_edge.render()


if __name__ == '__main__':
  mglw.run_window_config(PostProcessingDemo)