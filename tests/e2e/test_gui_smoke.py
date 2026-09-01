import pytest


pytestmark = [pytest.mark.e2e, pytest.mark.e2e_gui]


def test_desktop_gui_create_field_enter_record_and_open_records(qapp, quality_db_service):
    pytest.importorskip("PySide6")

    from core.services.language_service import LanguageService
    from data.repositories.field_repository_impl import FieldRepositoryImpl
    from data.repositories.project_repository_impl import ProjectRepositoryImpl
    from data.repositories.record_repository_impl import RecordRepositoryImpl
    from domain.entities.field_type import FieldType
    from presentation.theme.theme_service import ThemeService
    from presentation.viewmodels.field_viewmodel import FieldViewModel
    from presentation.viewmodels.project_viewmodel import ProjectViewModel
    from presentation.views.project_list_view import ProjectListView

    project_repo = ProjectRepositoryImpl(quality_db_service)
    field_repo = FieldRepositoryImpl(quality_db_service)

    language_service = LanguageService(qapp)
    theme_service = ThemeService(qapp)
    window = ProjectListView(
        ProjectViewModel(project_repo),
        FieldViewModel(field_repo),
        quality_db_service,
        language_service,
        theme_service,
    )

    window.name_input.setText("GUI E2E")
    window.add_btn.click()
    qapp.processEvents()
    assert window.project_list.count() == 1

    window.project_list.setCurrentRow(0)
    window.on_open_builder_clicked()
    qapp.processEvents()
    builder = window.form_builder_window
    assert builder is not None

    builder.name_input.setText("Age")
    integer_index = builder.type_combo.findData(FieldType.INTEGER)
    assert integer_index >= 0
    builder.type_combo.setCurrentIndex(integer_index)
    builder.required_check.setChecked(True)
    builder.add_btn.click()
    qapp.processEvents()
    assert builder.fields_list.count() == 1

    fields = field_repo.get_fields_by_project(builder.project_id)
    assert len(fields) == 1
    age_field = fields[0]

    builder.open_data_entry()
    qapp.processEvents()
    entry = builder.data_entry_window
    assert entry is not None
    entry.input_widgets[age_field.id].setText("25")
    entry.on_save(close_on_success=False)
    qapp.processEvents()

    records = RecordRepositoryImpl(quality_db_service).get_records_by_project(builder.project_id)
    assert len(records) == 1
    assert records[0].values[0].value == "25"

    builder.open_records_view()
    qapp.processEvents()
    records_window = builder.records_window
    assert records_window is not None
    assert records_window.table.rowCount() == 1

    records_window.close()
    entry.close()
    builder.close()
    window.close()
