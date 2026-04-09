"""상태/우선순위 필터 E2E 테스트."""
import re
import pytest


def _add_todo(page, title, priority="medium"):
    page.fill("#title", title)
    page.fill("#description", "설명")
    page.select_option("#priority", priority)
    page.click("button[type='submit']")
    page.wait_for_selector(f".todo-card.priority-{priority}", state="visible")


@pytest.mark.e2e
def test_filter_active_hides_completed(page):
    """'미완료' 필터 클릭 시 완료된 카드가 숨겨져야 한다."""
    _add_todo(page, "미완료 할 일")
    _add_todo(page, "완료 할 일")
    # 두 번째 카드 완료 처리
    page.locator(".toggle-check").nth(1).click()
    page.wait_for_selector(".todo-card.completed", state="visible")
    # '미완료' 필터 적용
    page.locator(".filter-btn", has_text="미완료").click()
    page.wait_for_function("document.querySelectorAll('.todo-card').length === 1")
    assert page.locator(".todo-card").count() == 1
    assert page.locator(".todo-card.completed").count() == 0


@pytest.mark.e2e
def test_filter_completed_shows_only_done(page):
    """'완료' 필터 클릭 시 완료된 카드만 표시되어야 한다."""
    _add_todo(page, "미완료 할 일")
    _add_todo(page, "완료 할 일")
    page.locator(".toggle-check").nth(1).click()
    page.wait_for_selector(".todo-card.completed", state="visible")
    page.get_by_role("button", name=re.compile(r"^완료$")).click()
    page.wait_for_function("document.querySelectorAll('.todo-card').length === 1")
    assert page.locator(".todo-card").count() == 1
    assert page.locator(".todo-card.completed").count() == 1


@pytest.mark.e2e
def test_filter_all_shows_everything(page):
    """'전체' 필터 클릭 시 모든 카드가 다시 표시되어야 한다."""
    _add_todo(page, "미완료 할 일")
    _add_todo(page, "완료 할 일")
    page.locator(".toggle-check").nth(1).click()
    page.wait_for_selector(".todo-card.completed", state="visible")
    page.locator(".filter-btn", has_text="미완료").click()
    page.wait_for_function("document.querySelectorAll('.todo-card').length === 1")
    page.locator(".filter-btn", has_text="전체").first.click()
    page.wait_for_function("document.querySelectorAll('.todo-card').length === 2")
    assert page.locator(".todo-card").count() == 2


@pytest.mark.e2e
def test_priority_filter_high_shows_only_high(page):
    """'높음' 우선순위 필터 시 높음 카드만 표시되어야 한다."""
    _add_todo(page, "높음 할 일", priority="high")
    _add_todo(page, "낮음 할 일", priority="low")
    page.locator(".pf-btn", has_text="높음").click()
    page.wait_for_function("document.querySelectorAll('.todo-card').length === 1")
    assert page.locator(".todo-card").count() == 1
    assert page.locator(".todo-card.priority-high").count() == 1


@pytest.mark.e2e
def test_priority_filter_all_restores_list(page):
    """'전체' 우선순위 필터 클릭 시 모든 카드가 복원되어야 한다."""
    _add_todo(page, "높음 할 일", priority="high")
    _add_todo(page, "낮음 할 일", priority="low")
    page.locator(".pf-btn", has_text="높음").click()
    page.wait_for_function("document.querySelectorAll('.todo-card').length === 1")
    page.locator(".pf-btn", has_text="전체").first.click()
    page.wait_for_function("document.querySelectorAll('.todo-card').length === 2")
    assert page.locator(".todo-card").count() == 2
