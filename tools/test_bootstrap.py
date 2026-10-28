import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Bootstrap(unittest.TestCase):
    def test_stdin_install_and_uninstall_clone_update_and_forward_arguments(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            fixture = root / 'fixture/tools'
            fixture.mkdir(parents=True)
            (fixture / 'manage.py').write_text('import json,sys; print(json.dumps(sys.argv[1:]))\n')
            binary = root / 'bin'
            binary.mkdir()
            git = binary / 'git'
            git.write_text('''#!/bin/sh
set -eu
printf '%s\n' "$*" >> "$FAKE_GIT_LOG"
case "$1" in
  clone)
    for last do :; done
    mkdir -p "$last/.git"
    cp -R "$BOOTSTRAP_FIXTURE/." "$last/"
    ;;
  -C)
    case "$3" in
      remote) echo "${FAKE_ORIGIN:-https://github.com/ESHAYAT102/horizon-emissive-ores.git}" ;;
      diff) exit "${FAKE_DIRTY:-0}" ;;
      pull) : ;;
      *) exit 2 ;;
    esac
    ;;
  *) exit 2 ;;
esac
''')
            git.chmod(0o755)
            env = dict(os.environ, PATH=f'{binary}:/usr/bin:/bin', HOME=str(root),
                       XDG_DATA_HOME=str(root / 'data'), BOOTSTRAP_FIXTURE=str(root / 'fixture'),
                       FAKE_GIT_LOG=str(root / 'git.log'))
            env.pop('HORIZON_EMISSIVE_ORES_SOURCE', None)
            def run(script, args=(), overrides=None):
                return subprocess.run(['/bin/sh', '-s', '--', *args], input=(ROOT / script).read_text(),
                                      cwd=root, env=dict(env, **(overrides or {})), text=True, capture_output=True)
            installed = run('install.sh', ['--textures', '/textures with spaces'])
            self.assertEqual(installed.returncode, 0, installed.stderr)
            self.assertEqual(json.loads(installed.stdout), ['install', '--textures', '/textures with spaces'])
            self.assertTrue((root / 'data/horizon-emissive-ores/source/.git').is_dir())
            removed = run('uninstall.sh')
            self.assertEqual(removed.returncode, 0, removed.stderr)
            self.assertEqual(json.loads(removed.stdout), ['uninstall'])
            self.assertIn('pull --ff-only origin main', (root / 'git.log').read_text())
            self.assertNotEqual(run('install.sh', overrides={'FAKE_ORIGIN': 'https://example.com/other.git'}).returncode, 0)
            self.assertNotEqual(run('install.sh', overrides={'FAKE_DIRTY': '1'}).returncode, 0)


if __name__ == '__main__':
    unittest.main()
