"""할 일 완료 토글 E2E 테스트."""
import pytest


def _add_todo(page, title="토글 테스트"):
    page.fill("#title", title)
    page.fill("#description", "설명")
    page.click("button[type='submit']")
    page.wait_for_selector(".todo-card", state="visible")


@pytest.mark.e2e
def test_toggle_marks_todo_completed(page):
    """체크박스 클릭 후 카드에 .completed 클래스가 추가되어야 한다."""
    _add_todo(page)
    page.locator(".toggle-check").first.click()
    page.wait_for_selector(".todo-card.completed", state="visible")
    assert page.locator(".todo-card.completed").count() == 1


@pytest.mark.e2e
def test_toggle_twice_restores_active_state(page):
    """체크박스를 두 번 클릭하면 .completed 클래스가 제거되어야 한다."""
    _add_todo(page)
    checkbox = page.locator(".toggle-check").first
    checkbox.click()
    page.wait_for_selector(".todo-card.completed", state="visible")
    checkbox.click()
    page.wait_for_function("document.querySelectorAll('.todo-card.completed').length === 0")
    assert page.locator(".todo-card.completed").count() == 0


@pytest.mark.e2e
def test_toggle_updates_stats_completed_count(page):
    """토글 후 #stat-completed 값이 1 증가해야 한다."""
    _add_todo(page)
    before = int(page.locator("#stat-completed").inner_text())
    page.locator(".toggle-check").first.click()
    page.wait_for_function(
        f"parseInt(document.getElementById('stat-completed').textContent) > {before}"
    )
    after = int(page.locator("#stat-completed").inner_text())
    assert after == before + 1
