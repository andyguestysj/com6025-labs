"""
Generates three placeholder textures for Lab 05 — Textures.
Run once from the repo root: python week05/generate_textures.py
Requires Pillow and numpy (both already installed for this module).
"""

from PIL import Image, ImageDraw
import numpy as np
import os

SIZE = 256


def make_diffuse():
  img = Image.new('RGB', (SIZE, SIZE))
  cells = 8
  cell_size = SIZE // cells
  color_a = (240, 160, 40)
  color_b = (255, 235, 205)
  for row in range(cells):
    for col in range(cells):
      color = color_a if (row + col) % 2 == 0 else color_b
      x0, y0 = col * cell_size, row * cell_size
      img.paste(color, (x0, y0, x0 + cell_size, y0 + cell_size))

  # A red band across the TOP only — this is what makes the
  # upside-down bug in Task 5 obvious rather than subtle.
  draw = ImageDraw.Draw(img)
  draw.rectangle([0, 0, SIZE, 28], fill=(200, 30, 30))
  draw.text((SIZE // 2 - 14, 6), 'TOP', fill=(255, 255, 255))
  return img


def make_detail():
  img = Image.new('RGB', (SIZE, SIZE), (235, 235, 235))
  draw = ImageDraw.Draw(img)
  spacing = 32
  radius = 6
  for cy in range(spacing // 2, SIZE, spacing):
    for cx in range(spacing // 2, SIZE, spacing):
      draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(90, 90, 90))
  return img


def make_normal():
  # A synthetic "bump" normal map: a radial dome, encoded as
  # tangent-space normals in RGB — this is what Weeks 6-7 will
  # perturb the lighting calculation with.
  xs = np.linspace(-1, 1, SIZE)
  ys = np.linspace(-1, 1, SIZE)
  x, y = np.meshgrid(xs, ys)
  dist = np.sqrt(x ** 2 + y ** 2)
  height = np.clip(0.8 - dist, 0.0, None) ** 2

  dzdx = np.gradient(height, axis=1)
  dzdy = np.gradient(height, axis=0)

  strength = 12.0
  nx, ny, nz = -dzdx * strength, -dzdy * strength, np.ones_like(height)
  length = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
  nx, ny, nz = nx / length, ny / length, nz / length

  r = ((nx * 0.5 + 0.5) * 255).astype(np.uint8)
  g = ((ny * 0.5 + 0.5) * 255).astype(np.uint8)
  b = ((nz * 0.5 + 0.5) * 255).astype(np.uint8)
  return Image.fromarray(np.dstack([r, g, b]), mode='RGB')


if __name__ == '__main__':
  os.makedirs('week05/textures', exist_ok=True)
  make_diffuse().save('week05/textures/diffuse.png')
  make_detail().save('week05/textures/detail.png')
  make_normal().save('week05/textures/normal.png')
  print('Saved diffuse.png, detail.png, normal.png to week05/textures/')
