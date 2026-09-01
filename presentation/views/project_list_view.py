from PySide6.QtCore import QEvent, QSize, Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from core.services.language_service import LanguageService
from presentation.theme.theme_service import ThemeService
from presentation.components.app_button import AppButton
from presentation.components.app_empty_state import AppEmptyState
from presentation.viewmodels.field_viewmodel import FieldViewModel
from presentation.viewmodels.project_viewmodel import ProjectViewModel
from presentation.views.form_builder_view import FormBuilderView


class ProjectListView(QWidget):
    """Quiet dashboard focused on the user's projects and next action."""

    def __init__(
        self,
        viewmodel: ProjectViewModel,
        field_viewmodel: FieldViewModel,
        db_service,
        language_service: LanguageService,
        theme_service: ThemeService,
    ):
        super().__init__()
        self.viewmodel = viewmodel
        self.field_viewmodel = field_viewmodel
        self.db_service = db_service
        self.language_service = language_service
        self.theme_service = theme_service
        self.form_builder_window = None

        self.setup_ui()
        self.setup_connections()
        self.setup_shortcuts()
        self.viewmodel.load_projects()

    def setup_ui(self):
        self.setObjectName("AppRoot")
        self.resize(980, 720)
        self.setMinimumSize(820, 600)

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 28)
        root.setSpacing(24)

        top_bar = QHBoxLayout()
        brand_box = QVBoxLayout()
        brand_box.setSpacing(1)
        self.brand_label = QLabel("Paper2Data")
        self.brand_label.setProperty("role", "brand")
        self.brand_tagline = QLabel()
        self.brand_tagline.setProperty("role", "helper")
        brand_box.addWidget(self.brand_label)
        brand_box.addWidget(self.brand_tagline)
        top_bar.addLayout(brand_box)
        top_bar.addStretch()

        self.language_label = QLabel()
        self.language_label.setProperty("role", "muted")
        self.language_combo = QComboBox()
        self.language_combo.setMinimumWidth(125)
        for code, display_name in self.language_service.available_languages().items():
            self.language_combo.addItem(display_name, userData=code)
        current_index = self.language_combo.findData(self.language_service.current_language)
        if current_index >= 0:
            self.language_combo.setCurrentIndex(current_index)

        self.theme_btn = AppButton(variant=AppButton.GHOST)
        self.theme_btn.setMinimumWidth(112)
        top_bar.addWidget(self.language_label)
        top_bar.addWidget(self.language_combo)
        top_bar.addWidget(self.theme_btn)
        root.addLayout(top_bar)

        hero = QVBoxLayout()
        hero.setSpacing(5)
        self.page_title = QLabel()
        self.page_title.setProperty("role", "pageTitle")
        self.page_subtitle = QLabel()
        self.page_subtitle.setProperty("role", "muted")
        self.page_subtitle.setWordWrap(True)
        hero.addWidget(self.page_title)
        hero.addWidget(self.page_subtitle)
        root.addLayout(hero)

        self.create_card = QFrame()
        self.create_card.setProperty("card", True)
        create_layout = QVBoxLayout(self.create_card)
        create_layout.setContentsMargins(22, 20, 22, 20)
        create_layout.setSpacing(12)

        create_head = QHBoxLayout()
        create_texts = QVBoxLayout()
        create_texts.setSpacing(2)
        self.create_title = QLabel()
        self.create_title.setProperty("role", "sectionTitle")
        self.create_helper = QLabel()
        self.create_helper.setProperty("role", "muted")
        create_texts.addWidget(self.create_title)
        create_texts.addWidget(self.create_helper)
        create_head.addLayout(create_texts)
        create_head.addStretch()
        create_layout.addLayout(create_head)

        create_row = QHBoxLayout()
        create_row.setSpacing(10)
        self.name_input = QLineEdit()
        self.name_input.setMinimumHeight(44)
        self.add_btn = AppButton(variant=AppButton.PRIMARY)
        self.add_btn.setMinimumHeight(44)
        create_row.addWidget(self.name_input, 1)
        create_row.addWidget(self.add_btn)
        create_layout.addLayout(create_row)
        root.addWidget(self.create_card)

        projects_header = QHBoxLayout()
        self.projects_title = QLabel()
        self.projects_title.setProperty("role", "sectionTitle")
        self.projects_count = QLabel()
        self.projects_count.setProperty("role", "muted")
        projects_header.addWidget(self.projects_title)
        projects_header.addWidget(self.projects_count)
        projects_header.addStretch()
        root.addLayout(projects_header)

        self.project_list = QListWidget()
        self.project_list.setSpacing(2)
        self.project_list.setUniformItemSizes(False)
        root.addWidget(self.project_list, 1)

        self.empty_state = AppEmptyState()
        self.empty_state.setProperty("card", True)
        root.addWidget(self.empty_state, 1)
        self.empty_state.hide()

        actions = QHBoxLayout()
        actions.addStretch()
        self.delete_btn = AppButton(variant=AppButton.DANGER)
        self.open_builder_btn = AppButton(variant=AppButton.PRIMARY)
        self.open_builder_btn.setMinimumWidth(210)
        actions.addWidget(self.delete_btn)
        actions.addWidget(self.open_builder_btn)
        root.addLayout(actions)

        self.retranslate_ui()
        self._update_theme_button()

    def setup_connections(self):
        self.add_btn.clicked.connect(self.on_add_clicked)
        self.name_input.returnPressed.connect(self.on_add_clicked)
        self.delete_btn.clicked.connect(self.on_delete_clicked)
        self.open_builder_btn.clicked.connect(self.on_open_builder_clicked)
        self.project_list.itemDoubleClicked.connect(lambda _item: self.on_open_builder_clicked())
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        self.theme_btn.clicked.connect(self.on_theme_toggle)
        self.empty_state.action_clicked.connect(self.name_input.setFocus)
        self.viewmodel.projects_loaded.connect(self.update_list)
        self.viewmodel.error_occurred.connect(self.show_error)
        self.theme_service.theme_changed.connect(lambda _mode: self._update_theme_button())

    def setup_shortcuts(self):
        shortcut_new = QShortcut(QKeySequence("Ctrl+N"), self)
        shortcut_new.activated.connect(self.name_input.setFocus)

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("Paper2Data - Project Management"))
        self.brand_tagline.setText(self.tr("From paper to data, simply."))
        self.language_label.setText(self.tr("Language:"))
        self.page_title.setText(self.tr("What do you want to do today?"))
        self.page_subtitle.setText(
            self.tr("Create a project, define the information on your paper forms, then enter records without dealing with spreadsheets.")
        )
        self.create_title.setText(self.tr("Create a new project"))
        self.create_helper.setText(self.tr("Start a clean data-entry workspace."))
        self.name_input.setPlaceholderText(self.tr("Example: Customer satisfaction survey"))
        self.add_btn.setText(self.tr("＋ Create Project"))
        self.projects_title.setText(self.tr("Your projects"))
        self.open_builder_btn.setText(self.tr("Open Project"))
        self.delete_btn.setText(self.tr("Delete"))
        self.empty_state.set_content(
            self.tr("No projects yet"),
            self.tr("Create your first project and start turning paper forms into structured data."),
            self.tr("＋ Create your first project"),
        )
        self._update_theme_button()
        self.viewmodel.load_projects()

    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange and hasattr(self, "add_btn"):
            self.retranslate_ui()
        super().changeEvent(event)

    def _update_theme_button(self):
        if not hasattr(self, "theme_btn"):
            return
        self.theme_btn.setText(
            self.tr("☀ Light mode") if self.theme_service.is_dark else self.tr("◐ Dark mode")
        )

    def on_theme_toggle(self):
        self.theme_service.toggle()

    def on_language_changed(self, index: int):
        lang_code = self.language_combo.itemData(index)
        if not lang_code or lang_code == self.language_service.current_language:
            return
        if self.language_service.switch_language(lang_code):
            return
        self.show_error(self.tr("Failed to switch language. Translation file not found."))
        self.language_combo.blockSignals(True)
        current_index = self.language_combo.findData(self.language_service.current_language)
        if current_index >= 0:
            self.language_combo.setCurrentIndex(current_index)
        self.language_combo.blockSignals(False)

    def on_add_clicked(self):
        name = self.name_input.text().strip()
        self.viewmodel.create_project(
            name=name,
            description=self.tr("Created via the interface"),
        )
        if name:
            self.name_input.clear()

    def on_delete_clicked(self):
        selected_item = self.project_list.currentItem()
        if selected_item:
            self.viewmodel.delete_project(selected_item.data(99))
            return
        self.show_error(self.tr("Please select a project to delete."))

    def on_open_builder_clicked(self):
        selected_item = self.project_list.currentItem()
        if not selected_item:
            self.show_error(self.tr("Please select a project first to build its form."))
            return

        self.form_builder_window = FormBuilderView(
            self.field_viewmodel,
            selected_item.data(99),
            selected_item.data(100),
            self.db_service,
        )
        self.form_builder_window.show()

    def update_list(self, projects):
        self.project_list.clear()
        for project in projects:
            date = project.updated_at or project.created_at or "—"
            record_count = int(getattr(project, "record_count", 0) or 0)
            item_text = "{name}\n{meta}".format(
                name=project.name,
                meta=self.tr("{count} records  •  Updated {date}").format(
                    count=record_count,
                    date=date,
                ),
            )
            item = QListWidgetItem(item_text)
            item.setSizeHint(QSize(100, 72))
            item.setData(99, project.id)
            item.setData(100, project.name)
            self.project_list.addItem(item)

        count = len(projects)
        self.projects_count.setText(self.tr("{count} total").format(count=count))
        has_projects = count > 0
        self.project_list.setVisible(has_projects)
        self.open_builder_btn.setVisible(has_projects)
        self.delete_btn.setVisible(has_projects)
        self.empty_state.setVisible(not has_projects)

    def show_error(self, message: str):
        QMessageBox.critical(self, self.tr("Error"), message)
