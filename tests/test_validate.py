import sys
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from validate import compare, read_xml, validate
from build import payload, build


class ValidationTests(unittest.TestCase):
    def test_release_layout_and_archive(self):
        import zipfile
        files = payload()
        self.assertIn('scenario/tutorial.xml', files)
        self.assertIn('conquest/CTW_World_Map_01_strings.xml', files)
        self.assertNotIn('conquest/CTW_World_Map_01.xml', files)
        self.assertFalse(any(p.startswith('mods/') or p.endswith('rise2.ini') for p in files))
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / 'release.zip'
            self.assertEqual(build(target), len(files))
            with zipfile.ZipFile(target) as z:
                self.assertIsNone(z.testzip())
                self.assertEqual(len(z.namelist()), len(files) + 1)
            with self.assertRaises(FileExistsError):
                build(target)

    def test_payload_parses_and_mirrors_match(self):
        count, errors = validate()
        self.assertGreater(count, 100)
        self.assertEqual(errors, [])

    def test_scoped_hashes_and_localized_names(self):
        original = ET.fromstring('<ROOT><FILE name="a"><STRING hash="1">$NUM0 apples</STRING></FILE><FILE name="b"><STRING hash="1">$NUM1 pears</STRING></FILE><SCORE_DATA name="King" score="5"/></ROOT>')
        translated = ET.fromstring('<ROOT><FILE name="a"><STRING hash="1">$NUM0 个苹果</STRING></FILE><FILE name="b"><STRING hash="1">$NUM1 个梨</STRING></FILE><SCORE_DATA name="国王" score="5"/></ROOT>')
        self.assertEqual(compare(translated, original), [])
        translated[0][0].text = '$NUM2 个苹果'
        self.assertTrue(any('placeholder' in e for e in compare(translated, original)))

    def test_missing_music_and_changed_scenario(self):
        original = ET.fromstring('<ROOT><TRACKS><SOUND file="a.wav"/><SOUND file="b.wav"/></TRACKS><SCENARIO id="t" file="t.scx"/></ROOT>')
        translated = ET.fromstring('<ROOT><TRACKS><SOUND file="a.wav"/></TRACKS><SCENARIO id="t" file="t.sce"/></ROOT>')
        errors = compare(translated, original)
        self.assertTrue(any('missing node' in e for e in errors))
        self.assertTrue(any('non-text attribute' in e for e in errors))

    def test_script_placeholder_types_and_resource_icons(self):
        original = ET.fromstring('<ROOT><STRING hash="1">$d0 Tribute #ICON3</STRING></ROOT>')
        translated = ET.fromstring('<ROOT><STRING hash="1">$s0 贡品 #ICON4</STRING></ROOT>')
        errors = compare(translated, original)
        self.assertTrue(any('placeholder' in e for e in errors))
        self.assertTrue(any('icon/color' in e for e in errors))
        translated[0].text = '$d0 贡品 #ICON3'
        self.assertEqual(compare(translated, original), [])

    def test_inline_markup_tail_is_validated(self):
        original = ET.fromstring('<ROOT><STRING>Unit<BULLET/>$NUM0 #ICON30</STRING></ROOT>')
        translated = ET.fromstring('<ROOT><STRING>单位<BULLET/>$NUM1 #ICON31</STRING></ROOT>')
        errors = compare(translated, original)
        self.assertTrue(any('placeholder' in e and '#tail' in e for e in errors))
        self.assertTrue(any('icon/color' in e and '#tail' in e for e in errors))

    def test_reviewed_gameplay_regressions(self):
        root = Path(__file__).resolve().parents[1]
        lookup = read_xml(root / 'Data/string_lookup.XML')
        def value(tree, key):
            return tree.find(f'.//STRING[@hash="{key}"]').text
        self.assertEqual(value(lookup, '169235689'), '使大不列颠的领土力量降低两级。')
        self.assertEqual(value(lookup, '3962092'), '每队 2 人')
        messages = read_xml(root / 'Data/translated_strings.xml')
        self.assertIn('多两支', value(messages, '1133089085'))
        coldwar = read_xml(root / 'mods/Chinese/conquest/ColdWar/scen_script_loc.XML')
        self.assertIn('$d0', value(coldwar, '521306082'))
        self.assertNotIn('$s0', value(coldwar, '521306082'))

    def test_printf_and_literal_percent(self):
        original = ET.fromstring('<ROOT><STRING hash="1">%d bytes, 20% faster</STRING></ROOT>')
        translated = ET.fromstring('<ROOT><STRING hash="1">%d 字节，速度加快 20%</STRING></ROOT>')
        self.assertEqual(compare(translated, original), [])
        translated[0].text = '%s 字节'
        self.assertTrue(any('printf' in e for e in compare(translated, original)))

    def test_encoding_error_and_entities_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'bad.xml'
            path.write_bytes(b'<?xml version="1.0" encoding="utf-8"?><ROOT>\xb7</ROOT>')
            with self.assertRaises(UnicodeError):
                read_xml(path)
            path.write_text('<!DOCTYPE ROOT [<!ENTITY x "value">]><ROOT>&x;</ROOT>')
            with self.assertRaises(ValueError):
                read_xml(path)


if __name__ == '__main__':
    unittest.main()
