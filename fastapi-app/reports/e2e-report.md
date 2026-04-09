# E2E 테스트 보고서

**실행 일시:** 2026-04-09 12:13:43

**전체:** 39  |  **통과:** 39  |  **실패:** 0  |  **건너뜀:** 0

## 결과 테이블

| 테스트 | 결과 | 소요시간 |
|--------|------|----------|
| `tests/e2e/test_add_todo.py::test_add_todo_appears_in_list` | ✅ PASS | 0.11s |
| `tests/e2e/test_add_todo.py::test_add_todo_shows_correct_title` | ✅ PASS | 0.10s |
| `tests/e2e/test_add_todo.py::test_add_todo_shows_priority_badge` | ✅ PASS | 0.13s |
| `tests/e2e/test_add_todo.py::test_add_todo_with_due_date` | ✅ PASS | 0.14s |
| `tests/e2e/test_add_todo.py::test_add_todo_default_priority_is_medium` | ✅ PASS | 0.13s |
| `tests/e2e/test_add_todo.py::test_form_clears_after_submit` | ✅ PASS | 0.12s |
| `tests/e2e/test_delete_todo.py::test_delete_removes_card_from_list` | ✅ PASS | 0.16s |
| `tests/e2e/test_delete_todo.py::test_delete_cancel_does_not_remove` | ✅ PASS | 0.64s |
| `tests/e2e/test_delete_todo.py::test_delete_updates_stats_total` | ✅ PASS | 0.17s |
| `tests/e2e/test_delete_todo.py::test_delete_last_todo_shows_empty_state` | ✅ PASS | 0.16s |
| `tests/e2e/test_edit_todo.py::test_edit_button_opens_modal` | ✅ PASS | 0.15s |
| `tests/e2e/test_edit_todo.py::test_edit_modal_prefills_values` | ✅ PASS | 0.15s |
| `tests/e2e/test_edit_todo.py::test_edit_save_updates_card_title` | ✅ PASS | 0.18s |
| `tests/e2e/test_edit_todo.py::test_edit_save_updates_priority_badge` | ✅ PASS | 0.19s |
| `tests/e2e/test_edit_todo.py::test_edit_cancel_closes_modal` | ✅ PASS | 0.17s |
| `tests/e2e/test_edit_todo.py::test_edit_modal_closes_on_backdrop_click` | ✅ PASS | 0.17s |
| `tests/e2e/test_filter.py::test_filter_active_hides_completed` | ✅ PASS | 0.24s |
| `tests/e2e/test_filter.py::test_filter_completed_shows_only_done` | ✅ PASS | 0.24s |
| `tests/e2e/test_filter.py::test_filter_all_shows_everything` | ✅ PASS | 0.25s |
| `tests/e2e/test_filter.py::test_priority_filter_high_shows_only_high` | ✅ PASS | 0.21s |
| `tests/e2e/test_filter.py::test_priority_filter_all_restores_list` | ✅ PASS | 0.22s |
| `tests/e2e/test_page_load.py::test_page_title_visible` | ✅ PASS | 0.01s |
| `tests/e2e/test_page_load.py::test_stats_dashboard_visible` | ✅ PASS | 0.01s |
| `tests/e2e/test_page_load.py::test_form_inputs_present` | ✅ PASS | 0.01s |
| `tests/e2e/test_page_load.py::test_filter_buttons_visible` | ✅ PASS | 0.01s |
| `tests/e2e/test_page_load.py::test_priority_filter_buttons_visible` | ✅ PASS | 0.01s |
| `tests/e2e/test_page_load.py::test_search_input_visible` | ✅ PASS | 0.01s |
| `tests/e2e/test_search.py::test_search_returns_matching_card` | ✅ PASS | 0.20s |
| `tests/e2e/test_search.py::test_search_hides_non_matching_cards` | ✅ PASS | 0.20s |
| `tests/e2e/test_search.py::test_search_reset_restores_list` | ✅ PASS | 0.22s |
| `tests/e2e/test_search.py::test_search_enter_key_triggers_search` | ✅ PASS | 0.16s |
| `tests/e2e/test_statistics.py::test_stats_total_increments_on_add` | ✅ PASS | 0.14s |
| `tests/e2e/test_statistics.py::test_stats_pending_decrements_after_toggle` | ✅ PASS | 0.17s |
| `tests/e2e/test_statistics.py::test_stats_completion_rate_updates` | ✅ PASS | 0.16s |
| `tests/e2e/test_statistics.py::test_priority_bar_high_count_shows` | ✅ PASS | 0.13s |
| `tests/e2e/test_statistics.py::test_stats_zero_on_empty_state` | ✅ PASS | 0.01s |
| `tests/e2e/test_toggle_todo.py::test_toggle_marks_todo_completed` | ✅ PASS | 0.17s |
| `tests/e2e/test_toggle_todo.py::test_toggle_twice_restores_active_state` | ✅ PASS | 0.21s |
| `tests/e2e/test_toggle_todo.py::test_toggle_updates_stats_completed_count` | ✅ PASS | 0.15s |
