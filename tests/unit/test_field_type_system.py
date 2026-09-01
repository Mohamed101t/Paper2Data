from domain.entities.field_type import FieldType
from domain.services.field_type_suggester import FieldTypeSuggester
from domain.services.field_value_codec import FieldValueCodec


def test_basic_catalog_is_shorter_than_full_catalog():
    assert len(FieldType.BASIC_TYPES) < len(FieldType.ALL)
    assert FieldType.SHORT_TEXT in FieldType.BASIC_TYPES
    assert FieldType.EMAIL in FieldType.BASIC_TYPES
    assert FieldType.CALCULATED in FieldType.ADDITIONAL_TYPES


def test_every_type_declares_storage_validation_and_export_rules():
    for field_type in FieldType.ALL:
        definition = FieldType.definition(field_type)
        assert definition.storage_kind
        assert definition.validation_rule
        assert definition.excel_kind
        assert definition.csv_kind
        assert definition.source_label
        assert definition.example


def test_field_name_suggestions_are_deterministic_and_multilingual():
    assert FieldTypeSuggester.suggest("تاريخ الميلاد") == FieldType.DATE
    assert FieldTypeSuggester.suggest("رقم الهاتف") == FieldType.PHONE_NUMBER
    assert FieldTypeSuggester.suggest("Salary") == FieldType.CURRENCY
    assert FieldTypeSuggester.suggest("Âge") == FieldType.INTEGER
    assert FieldTypeSuggester.suggest("工资") == FieldType.CURRENCY


def test_storage_codec_keeps_identifiers_as_text_and_normalizes_numbers():
    assert FieldValueCodec.normalize_for_storage(FieldType.IDENTIFIER, "00125") == "00125"
    assert FieldValueCodec.normalize_for_storage(FieldType.INTEGER, "025") == "25"
    assert FieldValueCodec.normalize_for_storage(FieldType.DECIMAL, "72,50") == "72.5"
    assert FieldValueCodec.normalize_for_storage(FieldType.PERCENTAGE, "85%") == "85"
    assert FieldValueCodec.normalize_for_storage(FieldType.YES_NO, "نعم") == "yes"
