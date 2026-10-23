"""Offline checks; optionally compare against a clean, locally owned Steam install."""
from __future__ import annotations

import argparse
from collections import Counter
import configparser
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
TOKENS = re.compile(r'\$(?:[A-Z][A-Z_0-9]*|[a-z]+[0-9]+)')
ICONS = re.compile(r'#(?:ICON|COLOR)[0-9]+')
# No space flag: otherwise prose such as "20% of" looks like a printf conversion.
PRINTF = re.compile(r'(?<![\d%])%(?:\d+\$)?[-+#0]*(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|ll|I64|[hlLwzjt])?[diuoxXfFeEgGaAcCsSpn]')
TEXT_ATTRIBUTES = {'title', 'subtitle', 'desc', 'intro', 'victory_conditions'}


def read_xml(path):
    raw = path.read_bytes()
    encoding = 'utf-16' if raw[:2] in (b'\xff\xfe', b'\xfe\xff') else 'utf-8-sig'
    text = raw.decode(encoding)
    if re.search(r'<!\s*(DOCTYPE|ENTITY)\b', text, re.I):
        raise ValueError('DTD/entity declarations are not allowed')
    if '\ufffd' in text:
        raise ValueError('Unicode replacement character found')
    # Legacy files legitimately declare encoding="unicode" and have a UTF-16 BOM.
    return ET.fromstring(text)


def nodes(root):
    result = {'ROOT': root}

    def visit(parent, path):
        counts = Counter()
        for child in parent:
            attrs = ('hash', 'id', 'index', 'res')
            if child.tag not in ('FONT', 'SCORE_DATA'):
                attrs += ('name',)
            key = child.tag + ''.join(f'[@{k}={child.get(k)}]' for k in attrs if k in child.attrib)
            counts[key] += 1
            child_path = f'{path}/{key}[{counts[key]}]'
            result[child_path] = child
            visit(child, child_path)
    visit(root, 'ROOT')
    return result


def compare(patch, base):
    errors = []
    actual, expected = nodes(patch), nodes(base)
    for key, original in expected.items():
        if key not in actual:
            errors.append(f'missing node: {key}')
            continue
        translated = actual[key]
        for attr in original.attrib.keys() | translated.attrib.keys():
            if attr in TEXT_ATTRIBUTES or (attr == 'name' and original.tag in ('ROOT', 'TRIBE', 'SCORE_DATA', 'FONT')):
                continue
            if attr == '{http://www.w3.org/XML/1998/namespace}space':
                continue
            if original.tag in ('FONT', 'RESOLUTION') and attr in ('filename', 'size', 'style', 'tex_size'):
                continue
            if original.tag == 'CODEPAGE' and attr == 'use_ea_line_breaking':
                continue
            if original.get(attr) != translated.get(attr):
                errors.append(f'changed non-text attribute: {key}/@{attr}')
        for attr in [None, '#tail'] + sorted(TEXT_ATTRIBUTES & original.attrib.keys()):
            a = (translated.text if attr is None else translated.tail if attr == '#tail' else translated.get(attr)) or ''
            b = (original.text if attr is None else original.tail if attr == '#tail' else original.get(attr)) or ''
            if Counter(TOKENS.findall(a)) != Counter(TOKENS.findall(b)):
                errors.append(f'placeholder mismatch: {key} {attr or "text"}')
            if Counter(ICONS.findall(a)) != Counter(ICONS.findall(b)):
                errors.append(f'icon/color mismatch: {key} {attr or "text"}')
            if PRINTF.findall(a) != PRINTF.findall(b):
                errors.append(f'printf mismatch: {key} {attr or "text"}')
    # Duplicated lookup keys are compared within each parent, never globally.
    for key in actual.keys() & expected.keys():
        for attr in ('hash',):
            a = Counter((n.tag, n.get(attr)) for n in actual[key] if n.get(attr))
            b = Counter((n.tag, n.get(attr)) for n in expected[key] if n.get(attr))
            for token, count in a.items():
                if count > max(1, b[token]):
                    errors.append(f'duplicate {attr}: {key} {token}')
    return errors


def validate(root=ROOT, game=None):
    errors = []
    count = 0
    for path in sorted(p for p in root.rglob('*') if p.suffix.lower() == '.xml'):
        rel = path.relative_to(root).as_posix()
        if not (rel.startswith('Data/') or rel.startswith('mods/Chinese/')):
            continue
        count += 1
        try:
            patch = read_xml(path)
        except (ValueError, ET.ParseError, UnicodeError) as exc:
            errors.append(f'{rel}: {exc}')
            continue
        for node in patch.iter():
            if node.tag == 'SCENARIO' and node.get('file', '').lower().endswith('.sce'):
                errors.append(f'{rel}: obsolete .sce scenario reference')
            if node.tag == 'FONT' and node.get('filename'):
                font = root / node.get('filename').replace('\\', '/')
                if not font.is_file():
                    errors.append(f'{rel}: missing font {font.name}')
        if game:
            original = game / rel.removeprefix('mods/Chinese/')
            if not original.is_file():
                errors.append(f'{rel}: original file not found')
            else:
                errors.extend(f'{rel}: {e}' for e in compare(patch, read_xml(original)))
            for node in patch.iter('SCENARIO'):
                target = node.get('file')
                if target and not (game / target.replace('\\', '/')).is_file():
                    errors.append(f'{rel}: missing scenario {target}')
    for path in (root / 'Data').rglob('*'):
        if path.is_file():
            mirror = root / 'mods/Chinese/Data' / path.relative_to(root / 'Data')
            if not mirror.is_file() or path.read_bytes() != mirror.read_bytes():
                errors.append(f'Data mirror differs: {path.name}')
    for path in (root / 'mods/Chinese/Data').rglob('*'):
        if path.is_file() and not (root / 'Data' / path.relative_to(root / 'mods/Chinese/Data')).is_file():
            errors.append(f'Unpaired mod Data file: {path.name}')
    for folder in (root / 'Data', root / 'mods'):
        for path in folder.rglob('*'):
            font_notice = path.parent.name == 'Fonts' and path.name in ('OFL.txt', 'SOURCES.txt')
            if path.is_file() and not font_notice and path.suffix.lower() not in ('.xml', '.ini', '.ttf', '.ttc', '.otf'):
                errors.append(f'Unexpected payload: {path.relative_to(root)}')
            if path.name.lower() == 'rise2.ini':
                errors.append('Display preferences must never be shipped')
    locale_path = Path('launcher_res/en/locale.ini')
    try:
        locale = configparser.ConfigParser(interpolation=None)
        locale.read_string((root / 'mods/Chinese' / locale_path).read_text(encoding='gbk'))
        if game:
            base = configparser.ConfigParser(interpolation=None)
            base.read_string((game / locale_path).read_text(encoding='utf-8-sig'))
            if set(locale.sections()) != set(base.sections()):
                errors.append('Launcher locale sections differ')
            for section in base.sections():
                if not locale.has_section(section) or set(locale[section]) != set(base[section]):
                    errors.append(f'Launcher locale keys differ: {section}')
                else:
                    for key in base[section]:
                        urls = lambda s: re.findall(r'https?://[^\s]+', s)
                        if urls(locale[section][key]) != urls(base[section][key]):
                            errors.append(f'Launcher locale URL differs: {section}/{key}')
    except (OSError, UnicodeError, configparser.Error) as exc:
        errors.append(f'Launcher locale: {exc}')
    return count, errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-dir', type=Path, help='Clean Steam game directory; never modified')
    args = parser.parse_args()
    count, errors = validate(game=args.game_dir)
    for error in errors:
        print(error)
    print(f'{count} XML files checked; {len(errors)} errors')
    sys.exit(bool(errors))
