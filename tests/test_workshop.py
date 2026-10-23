import sys
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from build_workshop import build_workshop


class WorkshopTests(unittest.TestCase):
    def test_publisher_paths_fonts_and_licenses(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'workshop.zip'
            count = build_workshop(target, workshop_id='3824946614')
            with zipfile.ZipFile(target) as archive:
                self.assertIsNone(archive.testzip())
                prefix = 'RON_zhCN_Compatibility/'
                names = {name.removeprefix(prefix) for name in archive.namelist() if name.startswith(prefix)}
                self.assertEqual(len(names), count)
                self.assertFalse(any('Data/Fonts/' in name or 'launcher_res/' in name or name.endswith('.ini') for name in names))
                for name in ('OFL.txt', 'SOURCES.txt', 'ATTRIBUTION.txt', 'Data/NotoSansCJKsc-Regular.otf', 'Data/NotoSansCJKsc-Bold.otf'):
                    self.assertIn(name, names)
                tree = ET.fromstring(archive.read(prefix + 'Data/fonts.xml'))
                for font in tree.iter('FONT'):
                    filename = font.get('filename', '')
                    if filename:
                        self.assertTrue(filename.startswith('..\\..\\workshop\\content\\287450\\3824946614\\Data\\'))
                        self.assertIn('Data/' + filename.split('\\')[-1], names)
                self.assertIn('Install-Workshop.ps1', archive.namelist())
            with self.assertRaises(FileExistsError):
                build_workshop(target)

    def test_reject_non_numeric_item_id(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'bad.zip'
            with self.assertRaises(ValueError):
                build_workshop(target, workshop_id='../bad')
            self.assertFalse(target.exists())
