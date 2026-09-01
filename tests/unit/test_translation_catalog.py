from pathlib import Path
from xml.etree import ElementTree as ET
import re

from domain.entities.field_type import FieldType


ROOT = Path(__file__).resolve().parents[2]
TRANSLATIONS_DIR = ROOT / "presentation" / "translations"
LANGUAGE_CODES = ("ar", "fr", "ru", "zh")


def _messages(code: str):
    path = TRANSLATIONS_DIR / f"paper2data_{code}.ts"
    root = ET.parse(path).getroot()
    return [message for message in root.findall(".//message")]


def test_four_non_base_translation_files_are_complete():
    source_sets = []
    for code in LANGUAGE_CODES:
        messages = _messages(code)
        assert messages
        assert all((message.findtext("translation") or "").strip() for message in messages)
        assert all(message.find("translation").get("type") != "unfinished" for message in messages)
        source_sets.append({message.findtext("source") for message in messages})

    assert all(source_set == source_sets[0] for source_set in source_sets[1:])


def test_all_41_field_type_labels_are_translated():
    expected_labels = {FieldType.source_label(field_type) for field_type in FieldType.ALL}
    for code in LANGUAGE_CODES:
        sources = {message.findtext("source") for message in _messages(code)}
        assert expected_labels <= sources


def test_translation_placeholders_match_source_placeholders():
    placeholder_pattern = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}")
    for code in LANGUAGE_CODES:
        for message in _messages(code):
            source = message.findtext("source") or ""
            translation = message.findtext("translation") or ""
            assert set(placeholder_pattern.findall(source)) == set(
                placeholder_pattern.findall(translation)
            ), (code, source, translation)
