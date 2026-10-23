import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_text import pairs, flags


class AuditTests(unittest.TestCase):
    def test_text_attributes_inline_tails_and_missing_translation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'patch'
            game = Path(directory) / 'game'
            (root / 'Data').mkdir(parents=True)
            (game / 'Data').mkdir(parents=True)
            (root / 'Data/a.xml').write_text('<ROOT title="标题"><STRING>文本<BULLET/>后续段落</STRING></ROOT>', encoding='utf-8')
            (game / 'Data/a.xml').write_text('<ROOT title="Title"><STRING>Text<BULLET/>Following paragraph</STRING><STRING>Missing text</STRING></ROOT>', encoding='utf-8')
            rows = list(pairs(game, root))
            self.assertEqual(len(rows), 4)
            self.assertTrue(any(r['en'] == 'Following paragraph' and r['zh'] == '后续段落' for r in rows))
            self.assertTrue(any('missing-text' in flags(r) for r in rows))

    def test_internal_english_name_is_not_a_missing_translation(self):
        row = {'key': 'ROOT/OPTION[1]/ENGLISH_NAME[1]', 'en': 'Next Spy', 'zh': 'Next Spy'}
        self.assertEqual(flags(row), 'technical-field;preserve-identifier')


if __name__ == '__main__':
    unittest.main()
