"""Export a private bilingual review CSV from a clean, locally owned install.

This is a candidate generator, not a translation quality certification.
Do not commit the exported original-game corpus to this repository.
"""
import argparse
from collections import Counter
import csv
import configparser
import json
from pathlib import Path
import re

from validate import ROOT, TOKENS, TEXT_ATTRIBUTES, nodes, read_xml


def pairs(game, root=ROOT):
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root).as_posix()
        if path.suffix.lower() != '.xml' or rel.startswith('mods/Chinese/Data/'):
            continue
        if not (rel.startswith('Data/') or rel.startswith('mods/Chinese/')):
            continue
        base = game / rel.removeprefix('mods/Chinese/')
        if not base.is_file():
            raise FileNotFoundError(base)
        actual, expected = nodes(read_xml(path)), nodes(read_xml(base))
        for key, original in expected.items():
            translated = actual.get(key)
            attributes = [None, '#tail'] + sorted(TEXT_ATTRIBUTES & original.attrib.keys())
            if original.tag in ('TRIBE', 'SCORE_DATA') and 'name' in original.attrib:
                attributes.append('name')
            for attr in attributes:
                en = (original.text if attr is None else original.tail if attr == '#tail' else original.get(attr)) or ''
                if not en.strip() or not re.search('[A-Za-z]', en):
                    continue
                zh = '' if translated is None else ((translated.text if attr is None else translated.tail if attr == '#tail' else translated.get(attr)) or '')
                yield {'file': rel, 'key': key + ('/@' + attr if attr else ''),
                       'en': en.strip(), 'zh': zh.strip()}
    locale = Path('launcher_res/en/locale.ini')
    if (root / 'mods/Chinese' / locale).is_file():
        base = configparser.ConfigParser(interpolation=None)
        translated = configparser.ConfigParser(interpolation=None)
        base.read_string((game / locale).read_text(encoding='utf-8-sig'))
        translated.read_string((root / 'mods/Chinese' / locale).read_text(encoding='gbk'))
        for section in base.sections():
            for key, text in base[section].items():
                yield {'file': 'mods/Chinese/' + locale.as_posix(),
                       'key': section + '/' + key, 'en': text,
                       'zh': translated.get(section, key, fallback='')}


def flags(row):
    en, zh = row['en'], row['zh']
    reasons = []
    technical = ('/ENGLISH_NAME[' in row['key'] or
                 row['key'].rsplit('/', 1)[-1].split('[')[0] in
                 {'REG_KEY', 'REG_KEY_TRIAL', 'BUILD_CONTINENT', 'UNIT_CONTINENT', 'BACKUP_BUILD_CONTINENT', 'CARD'})
    if technical:
        return 'technical-field;preserve-identifier'
    if not zh:
        reasons.append('missing-text')
    if en == zh and len(en.split()) >= 2:
        reasons.append('unchanged-English;review-context')
    if 'Text needed for' in zh:
        reasons.append('developer-fallback')
    def numbers(text):
        text = re.sub(r'#(?:ICON|COLOR)\d+', '', TOKENS.sub('', text))
        return Counter(re.findall(r'(?<![A-Za-z])\d+(?:\.\d+)?', text))
    if numbers(en) != numbers(zh):
        reasons.append('numeric-candidate;Chinese-number-words-may-be-valid')
    if en.count('%') != zh.count('%'):
        reasons.append('percent-candidate;wording-may-be-valid')
    return ';'.join(reasons)


def export(game, output, root=ROOT):
    rows = list(pairs(game, root))
    with output.open('x', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['file', 'key', 'en', 'zh', 'checks'])
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row, checks=flags(row)))
    return {'paired_records': len(rows),
            'unique_pairs': len({(r['en'], r['zh']) for r in rows}),
            'files': dict(sorted(Counter(r['file'] for r in rows).items())),
            'semantic_review': 'Not certified by this automated report'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.game_dir, args.output), ensure_ascii=False, indent=2))
