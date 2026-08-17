import sys
print(f"Python: {sys.version}")

import moderngl
ctx = moderngl.create_standalone_context()
print(f"OpenGL version code: {ctx.version_code}")
assert ctx.version_code >= 330, "OpenGL 3.3 or higher required"

import glm
m = glm.mat4(1.0)
assert m[0][0] == 1.0
print("PyGLM: OK")

from PIL import Image
print("Pillow: OK")

import pywavefront
print("pywavefront: OK")

import numpy as np
print(f"numpy {np.__version__}: OK")

print("\n✓ Everything looks good — you're ready for the module.")
