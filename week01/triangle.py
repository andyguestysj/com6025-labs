import moderngl_window as mglw
import numpy as np

def load_shader(path):
    with open(path, 'r') as f:
        return f.read()

class HelloTriangle(mglw.WindowConfig):
	gl_version = (3, 3)
	title = "COM6025M — Hello Triangle"
	window_size = (800, 600)
    
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.prog = self.ctx.program(
			vertex_shader=load_shader('week01/shaders/triangle.vert'),
			fragment_shader=load_shader('week01/shaders/triangle.frag'),
		)
  
		vertices = self.ctx.buffer(
			np.array([
				0.0,  0.6,   # top centre
				-0.6, -0.4,   # bottom left
				0.6, -0.4,   # bottom right
			], dtype='f4')    # 32-bit floats
		)	
  
		self.vao = self.ctx.vertex_array(self.prog, vertices, 'in_position')
  
	def on_render(self, time, frame_time):
		self.ctx.clear(0.1, 0.1, 0.1)   # dark grey background
		self.vao.render()
  
if __name__ == '__main__':
    mglw.run_window_config(HelloTriangle)
