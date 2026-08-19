"""
Generates a placeholder "gem" diffuse texture for Lab 08.
Run once from the repo root: python week08/generate_texture.py
"""
from PIL import Image, ImageDraw
import numpy as np
import os
import random

SIZE = 256


def make_gem_texture():
  xs = np.linspace(-1, 1, SIZE)
  ys = np.linspace(-1, 1, SIZE)
  x, y = np.meshgrid(xs, ys)
  dist = np.sqrt(x ** 2 + y ** 2)

  t = np.clip(dist, 0.0, 1.0)
  r = (60 + t * 40).astype(np.uint8)
  g = (20 + (1 - t) * 60).astype(np.uint8)
  b = (140 + (1 - t) * 100).astype(np.uint8)
  img = Image.fromarray(np.dstack([r, g, b]), mode='RGB')

  draw = ImageDraw.Draw(img)
  random.seed(8)
  for _ in range(40):
    cx = random.randint(0, SIZE - 1)
    cy = random.randint(0, SIZE - 1)
    radius = random.randint(1, 3)
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(255, 255, 255))

  return img


if __name__ == '__main__':
  os.makedirs('week08/textures', exist_ok=True)
  make_gem_texture().save('week08/textures/gem.png')
  print('Saved gem.png to week08/textures/')