from domain.entities.field import Field
from domain.entities.field_type import FieldType


def test_legacy_field_types_are_normalized():
    assert FieldType.normalize("Text") == FieldType.SHORT_TEXT
    assert FieldType.normalize("Number") == FieldType.DECIMAL
    assert FieldType.normalize("Phone") == FieldType.PHONE_NUMBER
    assert FieldType.normalize("Single Choice") == FieldType.SINGLE_CHOICE
    assert FieldType.normalize("Multiple Choice") == FieldType.MULTIPLE_CHOICE
    assert FieldType.normalize("Yes/No") == FieldType.YES_NO


def test_catalog_contains_41_common_types():
    assert len(FieldType.ALL) == 41
    assert len(set(FieldType.ALL)) == 41


def test_canonical_field_types_remain_unchanged():
    for field_type in FieldType.ALL:
        assert FieldType.normalize(field_type) == field_type


def test_field_entity_normalizes_legacy_database_value():
    field = Field(project_id=1, name="Age", field_type="Number")
    assert field.field_type == FieldType.DECIMAL


def test_choice_types_use_options():
    for field_type in {
        FieldType.SINGLE_CHOICE,
        FieldType.MULTIPLE_CHOICE,
        FieldType.DROPDOWN,
        FieldType.RADIO_BUTTONS,
        FieldType.CHECKBOXES,
    }:
        assert FieldType.uses_options(field_type)

    assert not FieldType.uses_options(FieldType.SHORT_TEXT)
    assert not FieldType.uses_options(FieldType.INTEGER)
