"""Build a PRIVATE .hmod from the player's textures; never publish its derived PNGs.

Usage: python3 tools/build_matched.py /path/to/resources/assets/minecraft/textures/block
Requires ImageMagick for PNG decoding and the adjacent cargo-horizon-mod build tool.
Source assets are untouched. Derived assets/packages stay under ignored .local/.
"""
import json
import argparse
import binascii
import os
from pathlib import Path
import shutil
import struct
import subprocess
import zlib

ROOT = Path(__file__).resolve().parents[1]
ORES = ['coal', 'iron', 'copper', 'gold', 'redstone', 'emerald', 'lapis', 'diamond']


def chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', binascii.crc32(kind + data))


def palette(pixels):
    return {tuple(pixels[i:i + 3]) for i in range(0, len(pixels), 4) if pixels[i + 3]}


def mineral_pixels(ore, rock, shared=frozenset(), kind='colored', coal_ceiling=0):
    """Exclude rock bevels as well as its base palette; preserve shared pale mineral highlights."""
    background = palette(rock)
    result = bytearray()
    for i in range(0, len(ore), 4):
        pixel = ore[i:i + 4]
        rgb = tuple(pixel[:3])
        high, low = max(rgb), min(rgb)
        if kind == 'coal':
            mineral = high <= coal_ceiling
        elif kind == 'quartz':
            # Red netherrack bevels are not quartz, even when absent from the plain rock palette.
            r, g, b = rgb
            mineral = r >= g >= b and r - g <= 2 * (g - b)
        else:
            # Pale highlights shared by stone/deepslate are mineral; variant-only, near-neutral
            # colours are rock bevels. Saturated variant-specific dark mineral shades stay lit.
            mineral = rgb in shared or (high > 0 and high - low >= high * 0.35)
        result.extend((*rgb, 255) if mineral and rgb not in background and pixel[3] else (0, 0, 0, 0))
    return bytes(result)


def encode(pixels, width, height):
    rows = b''.join(b'\0' + pixels[y * width * 4:(y + 1) * width * 4] for y in range(height))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(rows, 9)) + chunk(b'IEND', b''))


def read(path):
    dimensions = subprocess.check_output(['magick', 'identify', '-format', '%w %h', str(path)], text=True)
    width, height = map(int, dimensions.split())
    if not (1 <= width <= 64 and 1 <= height <= 64):
        raise ValueError(f'Unsupported texture dimensions: {path}: {dimensions}')
    pixels = subprocess.check_output(['magick', str(path), '-depth', '8', 'rgba:-'])
    if len(pixels) != width * height * 4:
        raise ValueError(f'Expected a single RGBA image: {path}')
    return pixels, width, height


def main(textures, tool):
    build = ROOT / '.local/texture-matched'
    build.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / 'src', build / 'src', dirs_exist_ok=True)
    shutil.copy2(ROOT / 'Cargo.toml', build / 'Cargo.toml')
    if (ROOT / 'Cargo.lock').exists():
        shutil.copy2(ROOT / 'Cargo.lock', build / 'Cargo.lock')
    shutil.copy2(ROOT / 'horizon-mod.toml', build / 'horizon-mod.toml')
    assets = build / 'assets/horizon_emissive_ores/textures/emissive'
    assets.mkdir(parents=True, exist_ok=True)
    pairs = [(f'{prefix}{ore}_ore', rock) for ore in ORES
             for prefix, rock in [('', 'stone'), ('deepslate_', 'deepslate')]]
    pairs.extend([('nether_gold_ore', 'netherrack'), ('nether_quartz_ore', 'netherrack')])
    coverage = {}
    shared_palettes = {}
    backgrounds = palette(read(textures / 'stone.png')[0]) | palette(read(textures / 'deepslate.png')[0])
    for ore in ORES:
        shared_palettes[ore] = (palette(read(textures / f'{ore}_ore.png')[0])
                                & palette(read(textures / f'deepslate_{ore}_ore.png')[0])) - backgrounds
    if not shared_palettes['coal']:
        raise ValueError('Cannot infer coal palette for these textures; a reviewed mask is required.')
    coal_ceiling = max(max(rgb) for rgb in shared_palettes['coal'])
    for name, rock_name in pairs:
        ore, width, height = read(textures / f'{name}.png')
        rock, _, _ = read(textures / f'{rock_name}.png')
        mineral = name.removeprefix('deepslate_').removeprefix('nether_').removesuffix('_ore')
        kind = mineral if mineral in ['coal', 'quartz'] else 'colored'
        pixels = mineral_pixels(ore, rock, shared_palettes.get(mineral, set()), kind, coal_ceiling)
        count = sum(pixels[i] != 0 for i in range(3, len(pixels), 4))
        if not 0 < count < width * height:
            raise ValueError(f'Cannot distinguish mineral from rock: {name}: {count} pixels')
        coverage[name] = count
        (assets / f'{name}.png').write_bytes(encode(pixels, width, height))
    subprocess.run([str(tool), 'build'], cwd=build, check=True,
                   env=dict(os.environ, CARGO_TARGET_DIR=str(build / 'target')))
    (build / 'coverage.json').write_text(json.dumps(coverage, indent=2) + '\n')
    print(json.dumps(coverage, indent=2))
    print('PRIVATE PACKAGE: ' + str(build / 'target/horizon-mod/horizon_emissive_ores.hmod'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('textures', type=Path)
    parser.add_argument('--tool', type=Path, required=True)
    args = parser.parse_args()
    main(args.textures.resolve(), args.tool.resolve())
