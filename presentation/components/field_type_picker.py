from typing import Callable, Optional

from PySide6.QtCore import QEvent, QSize
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from domain.entities.field_type import FieldType


class FieldTypePickerDialog(QDialog):
    """Visual, searchable field-type picker for non-technical users."""

    def __init__(
        self,
        label_resolver: Callable[[str], str],
        category_resolver: Callable[[str], str],
        parent=None,
    ):
        super().__init__(parent)
        self._label_resolver = label_resolver
        self._category_resolver = category_resolver
        self._selected_type: Optional[str] = None
        self._cards: dict[str, QToolButton] = {}

        self.setObjectName("AppRoot")
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 22)
        root.setSpacing(14)

        self.title_label = QLabel()
        self.title_label.setProperty("role", "pageTitle")
        self.subtitle_label = QLabel()
        self.subtitle_label.setProperty("role", "muted")
        self.subtitle_label.setWordWrap(True)
        self.search_input = QLineEdit()
        root.addWidget(self.title_label)
        root.addWidget(self.subtitle_label)
        root.addWidget(self.search_input)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.cards_container = QWidget()
        self.grid = QGridLayout(self.cards_container)
        self.grid.setContentsMargins(2, 4, 2, 4)
        self.grid.setHorizontalSpacing(10)
        self.grid.setVerticalSpacing(10)
        self.scroll.setWidget(self.cards_container)
        root.addWidget(self.scroll, 1)

        self.example_label = QLabel()
        self.example_label.setProperty("role", "helper")
        self.example_label.setWordWrap(True)
        root.addWidget(self.example_label)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        root.addWidget(self.buttons)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self._populate_cards()

        self.search_input.textChanged.connect(self._filter_cards)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.button_group.buttonClicked.connect(self._on_card_clicked)

        self.resize(720, 650)
        self.retranslate_ui()

    @property
    def selected_type(self) -> Optional[str]:
        return self._selected_type

    def _populate_cards(self) -> None:
        for index, field_type in enumerate(FieldType.ALL):
            card = QToolButton()
            card.setCheckable(True)
            card.setProperty("fieldTypeCard", True)
            card.setMinimumSize(QSize(185, 96))
            card.setMaximumHeight(110)
            card.setToolTip(FieldType.source_example(field_type))
            card.setProperty("fieldType", field_type)
            self.button_group.addButton(card)
            self._cards[field_type] = card
            row, column = divmod(index, 3)
            self.grid.addWidget(card, row, column)
        self._refresh_card_texts()

    def _symbol_for(self, field_type: str) -> str:
        category = FieldType.category(field_type)
        return {
            FieldType.CATEGORY_TEXT: "Aa",
            FieldType.CATEGORY_NUMBERS: "123",
            FieldType.CATEGORY_DATE_TIME: "◷",
            FieldType.CATEGORY_CHOICES: "✓",
            FieldType.CATEGORY_CONTACT: "@",
            FieldType.CATEGORY_LOCATION: "⌖",
            FieldType.CATEGORY_MEASUREMENT: "↕",
            FieldType.CATEGORY_FILES: "▣",
            FieldType.CATEGORY_IDENTIFIERS: "#",
            FieldType.CATEGORY_ADVANCED: "ƒx",
        }.get(category, "•")

    def _refresh_card_texts(self) -> None:
        for field_type, card in self._cards.items():
            card.setText(
                "{symbol}   {label}\n{example}".format(
                    symbol=self._symbol_for(field_type),
                    label=self._label_resolver(field_type),
                    example=FieldType.source_example(field_type),
                )
            )

    def retranslate_ui(self) -> None:
        self.setWindowTitle(self.tr("Choose Data Type"))
        self.title_label.setText(self.tr("What kind of information will you enter?"))
        self.subtitle_label.setText(
            self.tr("Choose by meaning and example. Paper2Data handles validation, storage and export automatically.")
        )
        self.search_input.setPlaceholderText(self.tr("Search types or examples..."))
        ok_button = self.buttons.button(QDialogButtonBox.StandardButton.Ok)
        cancel_button = self.buttons.button(QDialogButtonBox.StandardButton.Cancel)
        if ok_button:
            ok_button.setText(self.tr("Use this type"))
            ok_button.setEnabled(bool(self._selected_type))
        if cancel_button:
            cancel_button.setText(self.tr("Cancel"))
        self._refresh_card_texts()
        self._update_example()

    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange and hasattr(self, "cards_container"):
            self.retranslate_ui()
        super().changeEvent(event)

    def _filter_cards(self, text: str) -> None:
        query = text.strip().casefold()
        for field_type, card in self._cards.items():
            haystack = " ".join(
                (
                    self._label_resolver(field_type),
                    FieldType.source_label(field_type),
                    FieldType.source_example(field_type),
                    self._category_resolver(FieldType.category(field_type)),
                )
            ).casefold()
            card.setVisible(not query or query in haystack)

    def _on_card_clicked(self, button: QToolButton) -> None:
        self._selected_type = str(button.property("fieldType"))
        ok_button = self.buttons.button(QDialogButtonBox.StandardButton.Ok)
        if ok_button:
            ok_button.setEnabled(True)
        self._update_example()

    def _update_example(self) -> None:
        if not self._selected_type:
            self.example_label.setText(self.tr("Select a type to see how Paper2Data will treat it."))
            return
        self.example_label.setText(
            self.tr("Example: {example}  •  Category: {category}").format(
                example=FieldType.source_example(self._selected_type),
                category=self._category_resolver(FieldType.category(self._selected_type)),
            )
        )

    def accept(self) -> None:
        if self._selected_type:
            super().accept()
