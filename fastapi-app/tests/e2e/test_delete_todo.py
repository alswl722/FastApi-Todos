"""할 일 삭제 E2E 테스트."""
import pytest


def _add_todo(page, title="삭제 테스트"):
    page.fill("#title", title)
    page.fill("#description", "설명")
    page.click("button[type='submit']")
    page.wait_for_selector(".todo-card", state="visible")


@pytest.mark.e2e
def test_delete_removes_card_from_list(page):
    """삭제 확인 후 카드가 목록에서 사라져야 한다."""
    _add_todo(page)
    page.on("dialog", lambda d: d.accept())
    page.locator("button:has-text('삭제')").first.click()
    page.wait_for_function("document.querySelectorAll('.todo-card').length === 0")
    assert page.locator(".todo-card").count() == 0


@pytest.mark.e2e
def test_delete_cancel_does_not_remove(page):
    """삭제 취소 시 카드가 그대로 유지되어야 한다."""
    _add_todo(page)
    page.on("dialog", lambda d: d.dismiss())
    page.locator("button:has-text('삭제')").first.click()
    # dismiss 후 카드는 유지
    page.wait_for_timeout(500)
    assert page.locator(".todo-card").count() == 1


@pytest.mark.e2e
def test_delete_updates_stats_total(page):
    """삭제 후 #stat-total 이 감소해야 한다."""
    _add_todo(page)
    before = int(page.locator("#stat-total").inner_text())
    page.on("dialog", lambda d: d.accept())
    page.locator("button:has-text('삭제')").first.click()
    page.wait_for_function(
        f"parseInt(document.getElementById('stat-total').textContent) < {before}"
    )
    after = int(page.locator("#stat-total").inner_text())
    assert after == before - 1


@pytest.mark.e2e
def test_delete_last_todo_shows_empty_state(page):
    """마지막 할 일 삭제 후 빈 상태 메시지가 표시되어야 한다."""
    _add_todo(page)
    page.on("dialog", lambda d: d.accept())
    page.locator("button:has-text('삭제')").first.click()
    page.wait_for_selector(".empty-state", state="visible")
    assert page.locator(".empty-state").is_visible()
