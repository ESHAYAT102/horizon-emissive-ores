from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import manage


class Installation(unittest.TestCase):
    def test_install_upgrade_uninstall_preserve_other_mods_and_preferences(self):
        with tempfile.TemporaryDirectory() as scratch, redirect_stdout(io.StringIO()):
            root = Path(scratch)
            home = root / 'game'
            home.mkdir()
            (home / 'horizon-mods.txt').write_text(f'mod.other:true\nkey.other.action:key.keyboard.x\n mod.{manage.ID} :false\n')
            mods = home / 'horizon-mods'
            mods.mkdir()
            (mods / 'other.hmod').write_bytes(b'untouched')
            package = root / 'test.hmod'
            with zipfile.ZipFile(package, 'w') as archive:
                archive.writestr('horizon-mod.toml', f'id = "{manage.ID}"\n')
                archive.writestr('mod.wasm', b'test')
            manage.install_package(home, package)
            self.assertIn(f'mod.{manage.ID}:true', (home / 'horizon-mods.txt').read_text())
            preference = mods / '.horizon-mod-data' / manage.ID / 'enabled'
            self.assertFalse(preference.exists(), 'No second settings toggle should be created')
            preference.parent.mkdir(parents=True)
            preference.write_bytes(b'false')
            manage.install_package(home, package)
            self.assertEqual(preference.read_bytes(), b'false')
            self.assertEqual(len(list((home / '.horizon-mod-backups').glob('*/*.hmod'))), 1)
            manage.uninstall(home)
            manage.uninstall(home)
            self.assertFalse((mods / f'{manage.ID}.hmod').exists())
            self.assertEqual((mods / 'other.hmod').read_bytes(), b'untouched')
            self.assertEqual((home / 'horizon-mods.txt').read_text(), 'mod.other:true\nkey.other.action:key.keyboard.x\n')
            self.assertEqual(preference.read_bytes(), b'false')

    def test_wrong_package_does_not_touch_game_home(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            package = root / 'bad.hmod'
            with zipfile.ZipFile(package, 'w') as archive:
                archive.writestr('horizon-mod.toml', 'id = "other"\n')
            with self.assertRaises(ValueError):
                manage.install_package(root / 'game', package)
            self.assertFalse((root / 'game').exists())

    def test_selected_version_textures_win_over_other_versions(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            for name in ['selected', 'newer']:
                folder = root / f'versions/{name}/.local/horizon-client/26.3/assets/minecraft/textures/block'
                folder.mkdir(parents=True)
                (folder / 'copper_ore.png').touch()
            (root / 'settings.json').write_text(json.dumps({'selected': 'selected'}))
            with patch.dict(os.environ, HORIZON_LAUNCHER_HOME=str(root)):
                self.assertIn('/selected/', str(manage.textures()))


if __name__ == '__main__':
    unittest.main()
