"""통계 대시보드 E2E 테스트."""
import pytest


def _add_todo(page, title="통계 테스트", priority="medium"):
    page.fill("#title", title)
    page.fill("#description", "설명")
    page.select_option("#priority", priority)
    page.click("button[type='submit']")
    page.wait_for_selector(".todo-card", state="visible")


@pytest.mark.e2e
def test_stats_total_increments_on_add(page):
    """할 일 추가 후 #stat-total 이 0에서 1로 증가해야 한다."""
    assert page.locator("#stat-total").inner_text() == "0"
    _add_todo(page)
    page.wait_for_function(
        "parseInt(document.getElementById('stat-total').textContent) === 1"
    )
    assert page.locator("#stat-total").inner_text() == "1"


@pytest.mark.e2e
def test_stats_pending_decrements_after_toggle(page):
    """완료 토글 후 #stat-pending 이 감소해야 한다."""
    _add_todo(page)
    page.wait_for_function(
        "parseInt(document.getElementById('stat-pending').textContent) === 1"
    )
    before = int(page.locator("#stat-pending").inner_text())
    page.locator(".toggle-check").first.click()
    page.wait_for_function(
        f"parseInt(document.getElementById('stat-pending').textContent) < {before}"
    )
    after = int(page.locator("#stat-pending").inner_text())
    assert after == before - 1


@pytest.mark.e2e
def test_stats_completion_rate_updates(page):
    """완료 처리 후 #stat-rate 값이 변경되어야 한다."""
    _add_todo(page)
    page.wait_for_function(
        "document.getElementById('stat-rate').textContent === '0%'"
    )
    page.locator(".toggle-check").first.click()
    page.wait_for_function(
        "document.getElementById('stat-rate').textContent !== '0%'"
    )
    rate = page.locator("#stat-rate").inner_text()
    assert rate == "100%"


@pytest.mark.e2e
def test_priority_bar_high_count_shows(page):
    """높음 우선순위 할 일 추가 후 #cnt-high 가 1이 되어야 한다."""
    _add_todo(page, priority="high")
    page.wait_for_function(
        "parseInt(document.getElementById('cnt-high').textContent) === 1"
    )
    assert page.locator("#cnt-high").inner_text() == "1"


@pytest.mark.e2e
def test_stats_zero_on_empty_state(page):
    """할 일이 없을 때 모든 통계 수치가 0이어야 한다."""
    assert page.locator("#stat-total").inner_text() == "0"
    assert page.locator("#stat-completed").inner_text() == "0"
    assert page.locator("#stat-pending").inner_text() == "0"
    assert page.locator("#stat-rate").inner_text() == "0%"
    assert page.locator("#cnt-high").inner_text() == "0"
    assert page.locator("#cnt-medium").inner_text() == "0"
    assert page.locator("#cnt-low").inner_text() == "0"
