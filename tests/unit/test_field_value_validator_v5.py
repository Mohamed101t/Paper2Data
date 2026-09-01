import pytest

from domain.entities.field import Field
from domain.entities.field_type import FieldType
from domain.services.field_value_codec import FieldValueCodec
from domain.services.field_value_validator import FieldValueValidator


pytestmark = pytest.mark.unit


def _field(field_type: str, required: bool = False) -> Field:
    return Field(project_id=1, id=1, name="Test field", field_type=field_type, is_required=required)


@pytest.mark.parametrize(
    ("field_type", "value"),
    [
        (FieldType.INTEGER, "25"),
        (FieldType.DECIMAL, "72.5"),
        (FieldType.DECIMAL, "72,5"),
        (FieldType.CURRENCY, "$1,500.50"),
        (FieldType.PERCENTAGE, "85%"),
        (FieldType.DURATION, "02:30"),
        (FieldType.EMAIL, "name@example.com"),
        (FieldType.PHONE_NUMBER, "+249 912 345 678"),
        (FieldType.URL, "https://example.com"),
        (FieldType.NATIONAL_ID, "0001-2345"),
        (FieldType.COORDINATES, "15.5007, 32.5599"),
        (FieldType.WEIGHT, "75 kg"),
        (FieldType.RATING, "5"),
        (FieldType.SCALE, "10"),
    ],
)
def test_common_valid_values_are_accepted(field_type, value):
    assert FieldValueValidator.validate(_field(field_type), value) is None


@pytest.mark.parametrize(
    ("field_type", "value", "expected_code"),
    [
        (FieldType.INTEGER, "25.5", "integer"),
        (FieldType.DECIMAL, "abc", "decimal"),
        (FieldType.PERCENTAGE, "101", "percentage"),
        (FieldType.DURATION, "2:99", "duration"),
        (FieldType.EMAIL, "invalid-email", "email"),
        (FieldType.PHONE_NUMBER, "123", "phone"),
        (FieldType.URL, "javascript:alert(1)", "url"),
        (FieldType.COORDINATES, "91, 32", "coordinates"),
        (FieldType.MEASUREMENT, "180", "measurement"),
        (FieldType.RATING, "6", "rating"),
        (FieldType.SCALE, "11", "scale"),
    ],
)
def test_common_invalid_values_have_stable_error_codes(field_type, value, expected_code):
    issue = FieldValueValidator.validate(_field(field_type), value)
    assert issue is not None
    assert issue.code == expected_code


def test_required_field_rejects_blank_value():
    issue = FieldValueValidator.validate(_field(FieldType.SHORT_TEXT, required=True), "   ")
    assert issue is not None
    assert issue.code == "required"


@pytest.mark.parametrize(
    ("field_type", "value", "stored"),
    [
        (FieldType.INTEGER, "025", "25"),
        (FieldType.DECIMAL, "72,50", "72.5"),
        (FieldType.CURRENCY, "$1,500.50", "1500.5"),
        (FieldType.CURRENCY, "€1.500,50", "1500.5"),
        (FieldType.PERCENTAGE, "85%", "85"),
        (FieldType.YES_NO, "نعم", "yes"),
        (FieldType.YES_NO, "Non", "no"),
        (FieldType.IDENTIFIER, "00125", "00125"),
    ],
)
def test_storage_normalization_preserves_semantics(field_type, value, stored):
    assert FieldValueCodec.normalize_for_storage(field_type, value) == stored
