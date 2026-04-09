"""검색 기능 E2E 테스트."""
import pytest


def _add_todo(page, title, description="설명"):
    page.fill("#title", title)
    page.fill("#description", description)
    page.click("button[type='submit']")
    page.wait_for_selector(".todo-card", state="visible")


@pytest.mark.e2e
def test_search_returns_matching_card(page):
    """키워드 검색 후 일치하는 카드가 표시되어야 한다."""
    _add_todo(page, "파이썬 공부하기")
    _add_todo(page, "운동하기")
    page.fill("#search-input", "파이썬")
    page.click("button:has-text('검색')")
    page.wait_for_function("document.querySelectorAll('.todo-card').length === 1")
    assert page.locator(".todo-card").count() == 1
    assert "파이썬" in page.locator(".todo-title").inner_text()


@pytest.mark.e2e
def test_search_hides_non_matching_cards(page):
    """검색 후 일치하지 않는 카드는 숨겨져야 한다."""
    _add_todo(page, "파이썬 공부하기")
    _add_todo(page, "운동하기")
    page.fill("#search-input", "파이썬")
    page.click("button:has-text('검색')")
    page.wait_for_function("document.querySelectorAll('.todo-card').length === 1")
    titles = [t.inner_text() for t in page.locator(".todo-title").all()]
    assert all("파이썬" in t for t in titles)


@pytest.mark.e2e
def test_search_reset_restores_list(page):
    """'초기화' 클릭 후 전체 목록이 복원되어야 한다."""
    _add_todo(page, "파이썬 공부하기")
    _add_todo(page, "운동하기")
    page.fill("#search-input", "파이썬")
    page.click("button:has-text('검색')")
    page.wait_for_function("document.querySelectorAll('.todo-card').length === 1")
    page.click("button:has-text('초기화')")
    page.wait_for_function("document.querySelectorAll('.todo-card').length === 2")
    assert page.locator(".todo-card").count() == 2


@pytest.mark.e2e
def test_search_enter_key_triggers_search(page):
    """검색창에서 Enter 키 입력으로 검색이 실행되어야 한다."""
    _add_todo(page, "파이썬 공부하기")
    _add_todo(page, "운동하기")
    page.fill("#search-input", "운동")
    page.locator("#search-input").press("Enter")
    page.wait_for_function("document.querySelectorAll('.todo-card').length === 1")
    assert page.locator(".todo-card").count() == 1
    assert "운동" in page.locator(".todo-title").inner_text()
