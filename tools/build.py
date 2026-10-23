"""Build a direct-overlay ZIP for Steam 1.20; does not read or modify a game install."""
import argparse
from pathlib import Path
import zipfile

from validate import ROOT, validate


def payload(root=ROOT):
    files = {}
    for folder in (root / 'Data', root / 'mods/Chinese'):
        for path in sorted(folder.rglob('*')):
            if not path.is_file():
                continue
            relative = path.relative_to(root).as_posix().removeprefix('mods/Chinese/')
            # This unlocalized world definition is identical to the tested base
            # game. Do not shadow gameplay/map configuration with a language pack.
            if relative == 'conquest/CTW_World_Map_01.xml':
                continue
            if relative in files and files[relative].read_bytes() != path.read_bytes():
                raise ValueError(f'Conflicting duplicate payload: {relative}')
            files[relative] = path
    return files


def build(output, root=ROOT):
    _, errors = validate(root)
    if errors:
        raise ValueError('\n'.join(errors))
    files = payload(root)
    with zipfile.ZipFile(output, 'x', zipfile.ZIP_DEFLATED) as archive:
        for relative, path in sorted(files.items()):
            archive.write(path, relative)
        archive.write(root / 'INSTALL.zh-CN.md', 'INSTALL.zh-CN.md')
    return len(files)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    print(f'{build(args.output)} payload files packaged in {args.output}')
