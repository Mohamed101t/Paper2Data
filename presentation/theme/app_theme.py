from dataclasses import dataclass


@dataclass(frozen=True)
class ThemePalette:
    background: str
    surface: str
    surface_alt: str
    surface_hover: str
    text: str
    text_muted: str
    border: str
    primary: str
    primary_hover: str
    primary_soft: str
    success: str
    success_soft: str
    warning: str
    error: str
    error_soft: str
    focus: str


class AppTheme:
    """Paper2Data design tokens and global Qt stylesheet.

    The UI intentionally uses quiet surfaces, a single indigo accent and
    consistent spacing/radius rules. Screens should use widget properties
    (role/variant) instead of embedding one-off colors in view code.
    """

    LIGHT = ThemePalette(
        background="#F6F7FB",
        surface="#FFFFFF",
        surface_alt="#F1F3F8",
        surface_hover="#ECEFFD",
        text="#1F2430",
        text_muted="#687083",
        border="#E1E5EE",
        primary="#4F46E5",
        primary_hover="#4338CA",
        primary_soft="#EEF0FF",
        success="#16875B",
        success_soft="#E9F7F0",
        warning="#B7791F",
        error="#C63D4E",
        error_soft="#FFF0F2",
        focus="#7C73F0",
    )

    DARK = ThemePalette(
        background="#171920",
        surface="#20232C",
        surface_alt="#292D38",
        surface_hover="#313646",
        text="#F5F7FB",
        text_muted="#AEB5C5",
        border="#353A47",
        primary="#8B83FF",
        primary_hover="#9D96FF",
        primary_soft="#2D2B4A",
        success="#51C995",
        success_soft="#203A31",
        warning="#E4B85C",
        error="#FF7D8C",
        error_soft="#47272D",
        focus="#A39CFF",
    )

    # Spacing/radius tokens are documented here so custom components use the
    # same rhythm even when a value cannot be expressed through QSS variables.
    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 12
    SPACING_LG = 16
    SPACING_XL = 24
    SPACING_2XL = 32
    RADIUS_INPUT = 11
    RADIUS_CARD = 16
    RADIUS_DIALOG = 20

    @classmethod
    def stylesheet(cls, mode: str = "light") -> str:
        p = cls.DARK if mode == "dark" else cls.LIGHT
        return f"""
        QWidget {{
            color: {p.text};
            background: transparent;
            font-family: "Segoe UI Variable", "Noto Sans Arabic", "Segoe UI", sans-serif;
            font-size: 14px;
        }}
        QWidget#AppRoot {{ background-color: {p.background}; }}
        QDialog {{ background-color: {p.background}; }}

        QLabel[role="brand"] {{ font-size: 20px; font-weight: 700; color: {p.primary}; }}
        QLabel[role="pageTitle"] {{ font-size: 28px; font-weight: 700; }}
        QLabel[role="sectionTitle"] {{ font-size: 18px; font-weight: 650; }}
        QLabel[role="body"] {{ font-size: 14px; }}
        QLabel[role="muted"] {{ color: {p.text_muted}; }}
        QLabel[role="helper"] {{ color: {p.text_muted}; font-size: 12px; }}
        QLabel[role="success"] {{ color: {p.success}; font-weight: 600; }}
        QLabel[role="error"] {{ color: {p.error}; font-size: 12px; font-weight: 600; }}

        QFrame[card="true"] {{
            background-color: {p.surface};
            border: 1px solid {p.border};
            border-radius: {cls.RADIUS_CARD}px;
        }}
        QFrame[softCard="true"] {{
            background-color: {p.surface_alt};
            border: 1px solid {p.border};
            border-radius: {cls.RADIUS_CARD}px;
        }}
        QFrame[fieldError="true"] {{
            background-color: {p.error_soft};
            border: 1px solid {p.error};
            border-radius: {cls.RADIUS_CARD}px;
        }}

        QPushButton {{
            min-height: 38px;
            padding: 0 15px;
            border: 1px solid {p.border};
            border-radius: {cls.RADIUS_INPUT}px;
            background-color: {p.surface};
            font-weight: 600;
        }}
        QPushButton:hover {{ background-color: {p.surface_hover}; }}
        QPushButton:pressed {{ padding-top: 1px; }}
        QPushButton:disabled {{ color: {p.text_muted}; background-color: {p.surface_alt}; }}
        QPushButton[variant="primary"] {{
            color: white;
            background-color: {p.primary};
            border-color: {p.primary};
        }}
        QPushButton[variant="primary"]:hover {{ background-color: {p.primary_hover}; border-color: {p.primary_hover}; }}
        QPushButton[variant="soft"] {{
            color: {p.primary};
            background-color: {p.primary_soft};
            border-color: transparent;
        }}
        QPushButton[variant="ghost"] {{ background-color: transparent; border-color: transparent; }}
        QPushButton[variant="danger"] {{ color: {p.error}; background-color: {p.error_soft}; border-color: transparent; }}
        QPushButton[variant="success"] {{ color: {p.success}; background-color: {p.success_soft}; border-color: transparent; }}

        QLineEdit, QTextEdit, QComboBox, QDateEdit, QTimeEdit, QDateTimeEdit {{
            min-height: 40px;
            padding: 0 11px;
            border: 1px solid {p.border};
            border-radius: {cls.RADIUS_INPUT}px;
            background-color: {p.surface};
            selection-background-color: {p.primary};
        }}
        QTextEdit {{ padding-top: 9px; padding-bottom: 9px; }}
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus, QDateTimeEdit:focus {{
            border: 2px solid {p.focus};
        }}
        QLineEdit[validationError="true"], QTextEdit[validationError="true"], QComboBox[validationError="true"] {{
            border: 1px solid {p.error};
            background-color: {p.error_soft};
        }}
        QComboBox::drop-down {{ border: 0; width: 28px; }}
        QComboBox QAbstractItemView {{
            background-color: {p.surface};
            border: 1px solid {p.border};
            selection-background-color: {p.primary_soft};
            selection-color: {p.text};
            padding: 6px;
        }}

        QListWidget, QTableWidget {{
            background-color: {p.surface};
            border: 1px solid {p.border};
            border-radius: {cls.RADIUS_CARD}px;
            outline: 0;
            gridline-color: {p.border};
        }}
        QListWidget::item {{
            padding: 13px 14px;
            margin: 4px 6px;
            border-radius: 12px;
        }}
        QListWidget::item:hover {{ background-color: {p.surface_alt}; }}
        QListWidget::item:selected {{ background-color: {p.primary_soft}; color: {p.text}; }}
        QHeaderView::section {{
            background-color: {p.surface_alt};
            color: {p.text_muted};
            border: 0;
            border-bottom: 1px solid {p.border};
            padding: 10px;
            font-weight: 650;
        }}
        QTableWidget::item {{ padding: 8px; }}
        QTableWidget::item:selected {{ background-color: {p.primary_soft}; color: {p.text}; }}

        QCheckBox, QRadioButton {{ spacing: 8px; min-height: 30px; }}
        QScrollArea {{ border: 0; background: transparent; }}
        QScrollBar:vertical {{ background: transparent; width: 10px; margin: 3px; }}
        QScrollBar::handle:vertical {{ background: {p.border}; min-height: 30px; border-radius: 5px; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        QToolTip {{ background-color: {p.text}; color: {p.surface}; border: 0; padding: 6px 8px; }}

        QToolButton[fieldTypeCard="true"] {{
            background-color: {p.surface};
            border: 1px solid {p.border};
            border-radius: 14px;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        QToolButton[fieldTypeCard="true"]:hover {{ border-color: {p.focus}; background-color: {p.primary_soft}; }}
        QToolButton[fieldTypeCard="true"]:checked {{ border: 2px solid {p.primary}; background-color: {p.primary_soft}; }}
        """

    @staticmethod
    def repolish(widget) -> None:
        """Refresh dynamic QSS properties without scattering style code."""
        style = widget.style()
        style.unpolish(widget)
        style.polish(widget)
        widget.update()
