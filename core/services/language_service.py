from typing import Dict, Optional

from PySide6.QtCore import QCoreApplication, QSettings, QTranslator, Qt

from core.services.runtime_paths import RuntimePaths


class LanguageService:
    """Loads, switches, persists, and applies the application language."""

    SUPPORTED_LANGUAGES: Dict[str, str] = {
        "ar": "العربية",
        "en": "English",
        "fr": "Français",
        "ru": "Русский",
        "zh": "中文",
    }
    RTL_LANGUAGES = {"ar"}
    BASE_LANGUAGE = "en"
    DEFAULT_LANGUAGE = "ar"

    def __init__(self, app: QCoreApplication):
        self._app = app
        self._translator: Optional[QTranslator] = None
        self._current_language = self.BASE_LANGUAGE
        self._settings = QSettings("Paper2Data", "Paper2Data")
        self._translations_dir = RuntimePaths.resource("presentation/translations")

    @property
    def current_language(self) -> str:
        return self._current_language

    def initialize(self) -> str:
        saved_language = str(self._settings.value("language", self.DEFAULT_LANGUAGE))
        if self.switch_language(saved_language):
            return self._current_language
        self.switch_language(self.BASE_LANGUAGE)
        return self._current_language

    def available_languages(self) -> Dict[str, str]:
        available = {self.BASE_LANGUAGE: self.SUPPORTED_LANGUAGES[self.BASE_LANGUAGE]}
        for code, name in self.SUPPORTED_LANGUAGES.items():
            if code != self.BASE_LANGUAGE and self._translation_path(code).is_file():
                available[code] = name
        return available

    def is_rtl(self, lang_code: str) -> bool:
        return lang_code in self.RTL_LANGUAGES

    def switch_language(self, lang_code: str) -> bool:
        if lang_code not in self.SUPPORTED_LANGUAGES:
            return False

        if lang_code == self._current_language:
            self._apply_layout_direction(lang_code)
            return True

        if lang_code == self.BASE_LANGUAGE:
            self._remove_current_translator()
            self._set_current_language(lang_code)
            return True

        translator = QTranslator()
        qm_path = self._translation_path(lang_code)
        if not qm_path.is_file() or not translator.load(str(qm_path)):
            return False

        previous_translator = self._translator
        if not self._app.installTranslator(translator):
            return False
        if previous_translator is not None:
            self._app.removeTranslator(previous_translator)

        self._translator = translator
        self._set_current_language(lang_code)
        return True

    def _translation_path(self, lang_code: str):
        return self._translations_dir / f"paper2data_{lang_code}.qm"

    def _remove_current_translator(self) -> None:
        if self._translator is not None:
            self._app.removeTranslator(self._translator)
            self._translator = None

    def _set_current_language(self, lang_code: str) -> None:
        self._current_language = lang_code
        self._settings.setValue("language", lang_code)
        self._apply_layout_direction(lang_code)

    def _apply_layout_direction(self, lang_code: str) -> None:
        direction = Qt.RightToLeft if self.is_rtl(lang_code) else Qt.LeftToRight
        self._app.setLayoutDirection(direction)
