"""Install/uninstall only this mod. Build artifacts remain outside the source tree in Git."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ID = 'horizon_emissive_ores'
REV = '52f1ba398a8fa0419508eda3e3c02afac673d01a'
GIT = 'https://github.com/ESHAYAT102/horizon'


def data_home():
    return Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share'))


def game_home():
    return Path(os.environ.get('HORIZON_HOME', data_home() / 'horizon'))


def textures():
    launcher = Path(os.environ.get('HORIZON_LAUNCHER_HOME', data_home() / 'horizon-launcher'))
    versions = launcher / 'versions'
    try:
        selected = json.loads((launcher / 'settings.json').read_text()).get('selected')
    except (OSError, ValueError):
        selected = None
    candidates = sorted(versions.glob('*'), key=lambda p: p.stat().st_mtime, reverse=True)
    if selected and Path(selected).name == selected:
        candidates.insert(0, versions / selected)
    for version in candidates:
        for folder in sorted((version / '.local/horizon-client').glob('*/assets/minecraft/textures/block')):
            if (folder / 'copper_ore.png').is_file():
                return folder
    raise ValueError('Prepared textures not found. Pass --textures /path/to/assets/minecraft/textures/block.')


def write_atomic(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(content)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def set_enabled(home, enabled):
    path = home / 'horizon-mods.txt'
    old = path.read_text() if path.exists() else ''
    lines = [line for line in old.splitlines() if line.partition(':')[0].strip() != f'mod.{ID}']
    if enabled:
        lines.append(f'mod.{ID}:true')
    if enabled or path.exists():
        write_atomic(path, ('\n'.join(lines) + ('\n' if lines else '')).encode())


def install_package(home, package):
    with zipfile.ZipFile(package) as archive:
        import tomllib
        manifest = tomllib.loads(archive.read('horizon-mod.toml').decode())
        if manifest.get('id') != ID or 'mod.wasm' not in archive.namelist():
            raise ValueError('Not a Horizon Emissive Ores package.')
    destination = home / 'horizon-mods' / f'{ID}.hmod'
    if destination.exists():
        backup = home / '.horizon-mod-backups' / ('emissive-ores-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
        backup.mkdir(parents=True)
        shutil.copy2(destination, backup / destination.name)
    write_atomic(destination, package.read_bytes())
    set_enabled(home, True)
    # Enable effects on first install, but preserve an existing user's ON/OFF preference.
    preference = destination.parent / '.horizon-mod-data' / ID / 'enabled'
    if not preference.exists():
        write_atomic(preference, b'true')
    print(f'Installed {destination}. Restart Horizon to load textures.')


def uninstall(home):
    (home / 'horizon-mods' / f'{ID}.hmod').unlink(missing_ok=True)
    set_enabled(home, False)
    print('Uninstalled Emissive Ores. Saved settings kept. Restart Horizon.')


def install(home, texture_path):
    for command in ['cargo', 'rustc', 'magick']:
        if not shutil.which(command):
            raise ValueError(f'Missing {command}; install the prerequisites listed in README.md.')
    texture_path = texture_path.resolve() if texture_path else textures()
    if not (texture_path / 'copper_ore.png').is_file():
        raise ValueError(f'No ore textures in {texture_path}')
    target_lib = subprocess.check_output(['rustc', '--print', 'target-libdir', '--target', 'wasm32-unknown-unknown'], text=True).strip()
    if not list(Path(target_lib).glob('libstd*')):
        if not shutil.which('rustup'):
            raise ValueError('Install the wasm32-unknown-unknown Rust target with rustup first.')
        subprocess.run(['rustup', 'target', 'add', 'wasm32-unknown-unknown'], check=True)
    cache = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache')) / 'horizon-emissive-ores' / REV
    tool = Path(os.environ['HORIZON_MOD_TOOL']).resolve() if os.environ.get('HORIZON_MOD_TOOL') else cache / 'bin/cargo-horizon-mod'
    if not tool.is_file():
        if os.environ.get('HORIZON_MOD_TOOL'):
            raise ValueError(f'HORIZON_MOD_TOOL does not exist: {tool}')
        subprocess.run(['cargo', 'install', '--git', GIT, '--rev', REV, '--locked',
                        '--root', str(cache), 'cargo-horizon-mod'], check=True)
    subprocess.run([sys.executable, str(ROOT / 'tools/build_matched.py'), str(texture_path), '--tool', str(tool)], check=True)
    package = ROOT / '.local/texture-matched/target/horizon-mod' / f'{ID}.hmod'
    subprocess.run([str(tool), 'check', str(package)], check=True)
    install_package(home, package)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['install', 'uninstall'])
    parser.add_argument('--textures', type=Path)
    args = parser.parse_args()
    if args.action == 'install':
        install(game_home(), args.textures)
    else:
        uninstall(game_home())


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError, zipfile.BadZipFile) as error:
        sys.exit(f'Error: {error}')
