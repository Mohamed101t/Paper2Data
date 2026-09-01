from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class FieldTypeDefinition:
    """Metadata that defines one Paper2Data field type.

    The identifier is persisted in SQLite and never translated. Everything the
    UI needs to display is derived from source strings that can be translated.
    Export and validation behavior are described here instead of being inferred
    from translated labels.
    """

    identifier: str
    source_label: str
    category: str
    example: str
    storage_kind: str
    validation_rule: str
    excel_kind: str
    csv_kind: str
    is_basic: bool = False
    supports_options: bool = False
    is_multi_value: bool = False
    is_virtual: bool = False


class FieldType:
    """Stable field-type identifiers and the central type catalogue."""

    SHORT_TEXT = "short_text"
    LONG_TEXT = "long_text"
    INTEGER = "integer"
    DECIMAL = "decimal"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    DATE = "date"
    TIME = "time"
    DATE_TIME = "date_time"
    DURATION = "duration"
    YES_NO = "yes_no"
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    DROPDOWN = "dropdown"
    RADIO_BUTTONS = "radio_buttons"
    CHECKBOXES = "checkboxes"
    RATING = "rating"
    SCALE = "scale"
    PHONE_NUMBER = "phone_number"
    EMAIL = "email"
    URL = "url"
    IDENTIFIER = "identifier"
    NATIONAL_ID = "national_id"
    CODE = "code"
    POSTAL_CODE = "postal_code"
    ADDRESS = "address"
    COUNTRY = "country"
    STATE_PROVINCE = "state_province"
    CITY = "city"
    COORDINATES = "coordinates"
    MEASUREMENT = "measurement"
    WEIGHT = "weight"
    LENGTH_HEIGHT = "length_height"
    TEMPERATURE = "temperature"
    FILE_ATTACHMENT = "file_attachment"
    IMAGE = "image"
    SIGNATURE = "signature"
    BARCODE = "barcode"
    QR_CODE = "qr_code"
    CALCULATED = "calculated"
    AUTO_NUMBER = "auto_number"

    CATEGORY_TEXT = "text"
    CATEGORY_NUMBERS = "numbers"
    CATEGORY_DATE_TIME = "date_time"
    CATEGORY_CHOICES = "choices"
    CATEGORY_CONTACT = "contact"
    CATEGORY_LOCATION = "location"
    CATEGORY_MEASUREMENT = "measurement"
    CATEGORY_FILES = "files"
    CATEGORY_IDENTIFIERS = "identifiers"
    CATEGORY_ADVANCED = "advanced"

    _DEFINITIONS: Dict[str, FieldTypeDefinition] = {
        SHORT_TEXT: FieldTypeDefinition(SHORT_TEXT, "Short Text", CATEGORY_TEXT, "Mohamed Ahmed", "text", "text", "text", "text", True),
        LONG_TEXT: FieldTypeDefinition(LONG_TEXT, "Long Text", CATEGORY_TEXT, "Long notes...", "text", "text", "text", "text", True),
        INTEGER: FieldTypeDefinition(INTEGER, "Integer", CATEGORY_NUMBERS, "25", "integer", "integer", "integer", "integer", True),
        DECIMAL: FieldTypeDefinition(DECIMAL, "Decimal", CATEGORY_NUMBERS, "72.5", "decimal", "decimal", "decimal", "decimal", True),
        CURRENCY: FieldTypeDefinition(CURRENCY, "Currency", CATEGORY_NUMBERS, "1500.50", "decimal", "currency", "currency", "decimal", True),
        PERCENTAGE: FieldTypeDefinition(PERCENTAGE, "Percentage", CATEGORY_NUMBERS, "85%", "decimal", "percentage", "percentage", "decimal", True),
        DATE: FieldTypeDefinition(DATE, "Date", CATEGORY_DATE_TIME, "2026-09-01", "date", "date", "date", "iso_date", True),
        TIME: FieldTypeDefinition(TIME, "Time", CATEGORY_DATE_TIME, "08:30", "time", "time", "time", "iso_time", True),
        DATE_TIME: FieldTypeDefinition(DATE_TIME, "Date & Time", CATEGORY_DATE_TIME, "2026-09-01 14:30", "datetime", "datetime", "datetime", "iso_datetime", True),
        DURATION: FieldTypeDefinition(DURATION, "Duration", CATEGORY_DATE_TIME, "02:30", "duration", "duration", "text", "text"),
        YES_NO: FieldTypeDefinition(YES_NO, "Yes / No", CATEGORY_CHOICES, "Yes / No", "boolean", "yes_no", "boolean", "boolean", True),
        SINGLE_CHOICE: FieldTypeDefinition(SINGLE_CHOICE, "Single Choice", CATEGORY_CHOICES, "Option A", "option", "choice", "text", "text", True, True),
        MULTIPLE_CHOICE: FieldTypeDefinition(MULTIPLE_CHOICE, "Multiple Choice", CATEGORY_CHOICES, "A, B", "option_list", "choice", "text", "text", True, True, True),
        DROPDOWN: FieldTypeDefinition(DROPDOWN, "Dropdown", CATEGORY_CHOICES, "Country", "option", "choice", "text", "text", True, True),
        RADIO_BUTTONS: FieldTypeDefinition(RADIO_BUTTONS, "Radio Buttons", CATEGORY_CHOICES, "Education level", "option", "choice", "text", "text", False, True),
        CHECKBOXES: FieldTypeDefinition(CHECKBOXES, "Checkboxes", CATEGORY_CHOICES, "A, B", "option_list", "choice", "text", "text", False, True, True),
        RATING: FieldTypeDefinition(RATING, "Rating", CATEGORY_CHOICES, "4 / 5", "integer", "rating", "integer", "integer", True),
        SCALE: FieldTypeDefinition(SCALE, "Scale", CATEGORY_CHOICES, "8 / 10", "integer", "scale", "integer", "integer", True),
        PHONE_NUMBER: FieldTypeDefinition(PHONE_NUMBER, "Phone Number", CATEGORY_CONTACT, "+249912345678", "text", "phone", "text", "text", True),
        EMAIL: FieldTypeDefinition(EMAIL, "Email", CATEGORY_CONTACT, "name@example.com", "text", "email", "text", "text", True),
        URL: FieldTypeDefinition(URL, "URL", CATEGORY_CONTACT, "https://example.com", "text", "url", "text", "text"),
        IDENTIFIER: FieldTypeDefinition(IDENTIFIER, "Identifier / ID", CATEGORY_IDENTIFIERS, "00125", "text", "identifier", "text", "text", True),
        NATIONAL_ID: FieldTypeDefinition(NATIONAL_ID, "National ID", CATEGORY_IDENTIFIERS, "0001234567", "text", "national_id", "text", "text"),
        CODE: FieldTypeDefinition(CODE, "Code", CATEGORY_IDENTIFIERS, "EMP-001", "text", "code", "text", "text"),
        POSTAL_CODE: FieldTypeDefinition(POSTAL_CODE, "Postal Code", CATEGORY_IDENTIFIERS, "12345", "text", "postal_code", "text", "text"),
        ADDRESS: FieldTypeDefinition(ADDRESS, "Address", CATEGORY_LOCATION, "Street, city", "text", "text", "text", "text"),
        COUNTRY: FieldTypeDefinition(COUNTRY, "Country", CATEGORY_LOCATION, "Sudan", "text", "text", "text", "text"),
        STATE_PROVINCE: FieldTypeDefinition(STATE_PROVINCE, "State / Province", CATEGORY_LOCATION, "Khartoum", "text", "text", "text", "text"),
        CITY: FieldTypeDefinition(CITY, "City", CATEGORY_LOCATION, "Omdurman", "text", "text", "text", "text"),
        COORDINATES: FieldTypeDefinition(COORDINATES, "Latitude / Longitude", CATEGORY_LOCATION, "15.5007, 32.5599", "coordinates", "coordinates", "text", "text"),
        MEASUREMENT: FieldTypeDefinition(MEASUREMENT, "Measurement", CATEGORY_MEASUREMENT, "180 cm", "measurement", "measurement", "text", "text"),
        WEIGHT: FieldTypeDefinition(WEIGHT, "Weight", CATEGORY_MEASUREMENT, "75 kg", "measurement", "measurement", "text", "text"),
        LENGTH_HEIGHT: FieldTypeDefinition(LENGTH_HEIGHT, "Length / Height", CATEGORY_MEASUREMENT, "175 cm", "measurement", "measurement", "text", "text"),
        TEMPERATURE: FieldTypeDefinition(TEMPERATURE, "Temperature", CATEGORY_MEASUREMENT, "37.2 °C", "measurement", "measurement", "text", "text"),
        FILE_ATTACHMENT: FieldTypeDefinition(FILE_ATTACHMENT, "File Attachment", CATEGORY_FILES, "document.pdf", "path", "file", "text", "text"),
        IMAGE: FieldTypeDefinition(IMAGE, "Image", CATEGORY_FILES, "photo.jpg", "path", "file", "text", "text"),
        SIGNATURE: FieldTypeDefinition(SIGNATURE, "Signature", CATEGORY_FILES, "signature.png", "path", "file", "text", "text"),
        BARCODE: FieldTypeDefinition(BARCODE, "Barcode", CATEGORY_IDENTIFIERS, "123456789012", "text", "identifier", "text", "text"),
        QR_CODE: FieldTypeDefinition(QR_CODE, "QR Code", CATEGORY_IDENTIFIERS, "SAMPLE-QR-001", "text", "identifier", "text", "text"),
        CALCULATED: FieldTypeDefinition(CALCULATED, "Calculated Field", CATEGORY_ADVANCED, "BMI = weight / height²", "calculated", "calculated", "text", "text", False, False, False, True),
        AUTO_NUMBER: FieldTypeDefinition(AUTO_NUMBER, "Auto Number", CATEGORY_ADVANCED, "001, 002, 003", "auto_number", "auto_number", "integer", "integer", False, False, False, True),
    }

    ALL: Tuple[str, ...] = tuple(_DEFINITIONS.keys())
    BASIC_TYPES: Tuple[str, ...] = tuple(
        identifier for identifier, definition in _DEFINITIONS.items() if definition.is_basic
    )
    ADDITIONAL_TYPES: Tuple[str, ...] = tuple(
        identifier for identifier, definition in _DEFINITIONS.items() if not definition.is_basic
    )
    OPTION_TYPES = {identifier for identifier, definition in _DEFINITIONS.items() if definition.supports_options}
    MULTI_VALUE_TYPES = {identifier for identifier, definition in _DEFINITIONS.items() if definition.is_multi_value}
    FILE_TYPES = {FILE_ATTACHMENT, IMAGE, SIGNATURE}
    NUMERIC_TYPES = {INTEGER, DECIMAL, CURRENCY, PERCENTAGE, RATING, SCALE}
    MEASUREMENT_TYPES = {MEASUREMENT, WEIGHT, LENGTH_HEIGHT, TEMPERATURE}
    VIRTUAL_TYPES = {identifier for identifier, definition in _DEFINITIONS.items() if definition.is_virtual}

    _LEGACY_ALIASES = {
        "Text": SHORT_TEXT,
        "text": SHORT_TEXT,
        "Long Text": LONG_TEXT,
        "long_text": LONG_TEXT,
        "Number": DECIMAL,
        "number": DECIMAL,
        "Date": DATE,
        "date": DATE,
        "Phone": PHONE_NUMBER,
        "phone": PHONE_NUMBER,
        "Email": EMAIL,
        "email": EMAIL,
        "Single Choice": SINGLE_CHOICE,
        "single_choice": SINGLE_CHOICE,
        "Multiple Choice": MULTIPLE_CHOICE,
        "multiple_choice": MULTIPLE_CHOICE,
        "Yes/No": YES_NO,
        "yes_no": YES_NO,
    }

    @classmethod
    def normalize(cls, value: str | None) -> str:
        if value is None:
            return cls.SHORT_TEXT
        if value in cls._DEFINITIONS:
            return value
        return cls._LEGACY_ALIASES.get(value, value)

    @classmethod
    def definition(cls, value: str | None) -> FieldTypeDefinition:
        normalized = cls.normalize(value)
        return cls._DEFINITIONS.get(normalized, cls._DEFINITIONS[cls.SHORT_TEXT])

    @classmethod
    def uses_options(cls, value: str | None) -> bool:
        return cls.definition(value).supports_options

    @classmethod
    def is_multiple_choice(cls, value: str | None) -> bool:
        return cls.definition(value).is_multi_value

    @classmethod
    def is_file_type(cls, value: str | None) -> bool:
        return cls.normalize(value) in cls.FILE_TYPES

    @classmethod
    def is_virtual(cls, value: str | None) -> bool:
        return cls.definition(value).is_virtual

    @classmethod
    def source_label(cls, value: str | None) -> str:
        return cls.definition(value).source_label

    @classmethod
    def source_example(cls, value: str | None) -> str:
        return cls.definition(value).example

    @classmethod
    def category(cls, value: str | None) -> str:
        return cls.definition(value).category
