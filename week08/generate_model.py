"""
Generates a small placeholder OBJ model: an 8-faced "gem" (a bipyramid),
written out in plain Wavefront OBJ text (v / vt / vn / f) — standing in
for a model exported from Blender, without needing a binary asset in the repo.
Run once from the repo root: python week08/generate_model.py
"""
import numpy as np
import os

R = 0.6
H = 1.0

apex_top = np.array([0.0, H, 0.0])
apex_bottom = np.array([0.0, -H, 0.0])
equator = [
  np.array([R, 0.0, 0.0]),
  np.array([0.0, 0.0, R]),
  np.array([-R, 0.0, 0.0]),
  np.array([0.0, 0.0, -R]),
]


def face_normal(a, b, c):
  n = np.cross(b - a, c - a)
  return n / np.linalg.norm(n)


def ensure_outward(a, b, c, uv_a, uv_b, uv_c, n):
  centroid = (a + b + c) / 3.0
  if np.dot(n, centroid) < 0:
    return (a, c, b), (uv_a, uv_c, uv_b), -n
  return (a, b, c), (uv_a, uv_b, uv_c), n


positions, uvs, normals, faces = [], [], [], []
UV_APEX_TOP = (0.5, 1.0)
UV_APEX_BOTTOM = (0.5, 0.0)


def add_face(a, b, c, uv_a, uv_b, uv_c):
  n = face_normal(a, b, c)
  (a, b, c), (uv_a, uv_b, uv_c), n = ensure_outward(a, b, c, uv_a, uv_b, uv_c, n)
  base = len(positions)
  for p, uv in zip((a, b, c), (uv_a, uv_b, uv_c)):
    positions.append(p)
    uvs.append(uv)
  normals.append(n)
  faces.append([
    (base + 1, base + 1, len(normals)),
    (base + 2, base + 2, len(normals)),
    (base + 3, base + 3, len(normals)),
  ])


for i in range(4):
  e_a = equator[i]
  e_b = equator[(i + 1) % 4]
  u_a = (i / 4.0, 0.5)
  u_b = ((i + 1) / 4.0, 0.5)
  add_face(apex_top, e_a, e_b, UV_APEX_TOP, u_a, u_b)
  add_face(apex_bottom, e_b, e_a, UV_APEX_BOTTOM, u_b, u_a)

lines = ['# Procedurally generated placeholder gem model for Lab 08', '# v/vt/vn/f only — triangles, no materials']
for p in positions:
  lines.append(f'v {p[0]:.6f} {p[1]:.6f} {p[2]:.6f}')
for uv in uvs:
  lines.append(f'vt {uv[0]:.6f} {uv[1]:.6f}')
for n in normals:
  lines.append(f'vn {n[0]:.6f} {n[1]:.6f} {n[2]:.6f}')
for f in faces:
  ref = ' '.join(f'{v}/{vt}/{vn}' for v, vt, vn in f)
  lines.append(f'f {ref}')

if __name__ == '__main__':
  os.makedirs('week08/models', exist_ok=True)
  with open('week08/models/gem.obj', 'w') as fh:
    fh.write('\n'.join(lines) + '\n')
  print(f'Saved week08/models/gem.obj — {len(positions)} vertices, {len(faces)} faces')


