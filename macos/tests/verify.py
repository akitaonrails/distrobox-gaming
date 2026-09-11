#!/usr/bin/env python3
"""Integration test: isolated paths, real Ansible execution, no app installation."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

source = Path(__file__).resolve().parents[1] / 'ansible'
with tempfile.TemporaryDirectory(prefix='dg-macos-test-') as temporary:
    root = Path(temporary)
    playbooks = root / 'ansible'
    shutil.copytree(source, playbooks)
    home = root / 'ES-DE & test'
    roms = root / 'ROMs & games'
    override = root / 'external PS2'
    settings = {'dg_macos_esde_home': str(home), 'dg_macos_rom_root': str(roms),
                'dg_macos_rom_paths': {'ps2': str(override)}}
    (playbooks / 'host_vars/localhost.yml').write_text(json.dumps(settings))
    command = ['ansible-playbook', '-i', 'localhost,', str(playbooks / 'site.yml')]
    env = dict(os.environ, ANSIBLE_NOCOLOR='1')

    def run(*arguments):
        result = subprocess.run(command + list(arguments), env=env, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode:
            raise RuntimeError(result.stdout)
        return result.stdout

    run('--syntax-check')
    run('--check', '--diff')
    assert not home.exists(), 'Check mode wrote configuration'
    target = home / 'custom_systems/es_systems.xml'
    target.parent.mkdir(parents=True)
    target.write_text('<systemList><!-- existing user configuration --></systemList>')
    run()
    assert any('existing user configuration' in f.read_text()
               for f in target.parent.glob('es_systems.xml.*')), 'No backup of previous config'
    tree = ET.parse(target)
    systems = {s.findtext('name'): s for s in tree.findall('system')}
    assert set(systems) == {'gc', 'wii', 'ps2', 'psp', 'atari2600', 'atari2600homebrew', 'nes', 'snes', 'mastersystem', 'megadrive', 'gba', 'gbc', 'c64'}
    assert systems['ps2'].findtext('path') == str(override), 'Host override ignored'
    assert systems['gc'].findtext('path') == str(roms / 'gc'), 'XML escaping corrupted path'
    assert all('(Standalone)' in systems[s].find('command').get('label')
               for s in ('gc', 'wii', 'ps2', 'psp')), 'Standalone label lost'
    assert 'stella_libretro.dylib' in systems['atari2600'].findtext('command')
    assert '.zip' not in systems['atari2600'].findtext('extension')
    assert systems['atari2600homebrew'].findtext('theme') == 'atari2600'
    assert not roms.exists() and not override.exists(), 'Created absent library mount'
    second = run()
    assert re.search(r'changed=0\s', second), second
    run('-e', 'dg_macos_create_rom_dirs=true')
    assert (roms / 'gc').is_dir() and override.is_dir()
    print('PASS: check mode, backups, XML escaping, host overrides, missing volumes, idempotence, opt-in directories')
