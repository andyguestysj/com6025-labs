"""
Generates a placeholder PBR material set for Lab 10 — albedo, roughness,
metallic, and ambient occlusion maps — plus a normal map using the same
approach as Week 5's normal.png.
Run once from the repo root: python week10/generate_pbr_textures.py
"""
from PIL import Image
import numpy as np
import os

SIZE = 256


def make_albedo():
  xs = np.linspace(0, 1, SIZE)
  ys = np.linspace(0, 1, SIZE)
  x, y = np.meshgrid(xs, ys)
  streaks = 0.05 * np.sin(y * 120.0)
  base = np.clip(0.55 + streaks, 0.0, 1.0)
  arr = (base * 255).astype(np.uint8)
  return Image.fromarray(np.dstack([arr, arr, arr]), mode='RGB')


def make_roughness():
  xs = np.linspace(0.05, 0.95, SIZE)
  row = (xs * 255).astype(np.uint8)
  arr = np.tile(row, (SIZE, 1))
  return Image.fromarray(np.dstack([arr, arr, arr]), mode='RGB')


def make_metallic():
  arr = np.zeros((SIZE, SIZE), dtype=np.uint8)
  arr[:, SIZE // 2:] = 255
  return Image.fromarray(np.dstack([arr, arr, arr]), mode='RGB')


def make_ao():
  xs = np.linspace(-1, 1, SIZE)
  ys = np.linspace(-1, 1, SIZE)
  x, y = np.meshgrid(xs, ys)
  dist = np.sqrt(x ** 2 + y ** 2)
  ao = np.clip(1.0 - 0.4 * dist, 0.5, 1.0)
  arr = (ao * 255).astype(np.uint8)
  return Image.fromarray(np.dstack([arr, arr, arr]), mode='RGB')


def make_normal():
  xs = np.linspace(-1, 1, SIZE)
  ys = np.linspace(-1, 1, SIZE)
  x, y = np.meshgrid(xs, ys)
  dist = np.sqrt(x ** 2 + y ** 2)
  height = np.clip(0.8 - dist, 0.0, None) ** 2

  dzdx = np.gradient(height, axis=1)
  dzdy = np.gradient(height, axis=0)

  strength = 8.0
  nx, ny, nz = -dzdx * strength, -dzdy * strength, np.ones_like(height)
  length = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
  nx, ny, nz = nx / length, ny / length, nz / length

  r = ((nx * 0.5 + 0.5) * 255).astype(np.uint8)
  g = ((ny * 0.5 + 0.5) * 255).astype(np.uint8)
  b = ((nz * 0.5 + 0.5) * 255).astype(np.uint8)
  return Image.fromarray(np.dstack([r, g, b]), mode='RGB')


if __name__ == '__main__':
  os.makedirs('week10/textures', exist_ok=True)
  make_albedo().save('week10/textures/albedo.png')
  make_roughness().save('week10/textures/roughness.png')
  make_metallic().save('week10/textures/metallic.png')
  make_ao().save('week10/textures/ao.png')
  make_normal().save('week10/textures/normal.png')
  print('Saved albedo/roughness/metallic/ao/normal.png to week10/textures/')