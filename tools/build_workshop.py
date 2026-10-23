"""Build an unpublished local Workshop candidate, never install or upload it."""
import argparse
from pathlib import Path
import zipfile
from build import payload
from validate import ROOT, validate


def build_workshop(output, root=ROOT, workshop_id=None):
    _, errors = validate(root)
    if errors:
        raise ValueError('\n'.join(errors))
    files = {name: path for name, path in payload(root).items()
             if not name.startswith('launcher_res/')}
    if workshop_id is not None and (not str(workshop_id).isdigit() or int(workshop_id) <= 0):
        raise ValueError('workshop_id must be a positive numeric Steam item ID')
    font_prefix = (f'..\\..\\workshop\\content\\287450\\{workshop_id}\\Data\\'
                   if workshop_id else 'mods\\RON_zhCN_Compatibility\\Data\\')
    with zipfile.ZipFile(output, 'x', zipfile.ZIP_DEFLATED) as archive:
        for name, path in sorted(files.items()):
            # RoN's publisher ignores Data/Fonts, including font/license files.
            target = name
            if name.startswith('Data/Fonts/'):
                target = ('Data/' if path.suffix.lower() == '.otf' else '') + path.name
            if name == 'Data/fonts.xml':
                xml = path.read_text(encoding='utf-8').replace('Data\\Fonts\\', font_prefix)
                archive.writestr('RON_zhCN_Compatibility/' + target, xml.encode('utf-8'))
            else:
                archive.write(path, 'RON_zhCN_Compatibility/' + target)
        archive.write(root / 'WORKSHOP-ATTRIBUTION.txt', 'RON_zhCN_Compatibility/ATTRIBUTION.txt')
        # Keep preparation notes outside the actual upload directory.
        archive.write(root / 'WORKSHOP.zh-CN.md', 'READ-BEFORE-PUBLISH.zh-CN.md')
        archive.write(root / 'tools/Install-Workshop.ps1', 'Install-Workshop.ps1')
    return len(files) + 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--workshop-id', help='Existing private/published item to update; never create a duplicate')
    args = parser.parse_args()
    print(f'{build_workshop(args.output, workshop_id=args.workshop_id)} payload files; no upload performed')
