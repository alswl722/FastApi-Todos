"""할 일 추가 기능 E2E 테스트."""
import pytest


def _add_todo(page, title="테스트 할 일", description="설명입니다", priority=None, due_date=None):
    """폼에 데이터를 입력하고 제출하는 헬퍼."""
    page.fill("#title", title)
    page.fill("#description", description)
    if priority:
        page.select_option("#priority", priority)
    if due_date:
        page.fill("#due_date", due_date)
    page.click("button[type='submit']")
    # 카드가 목록에 나타날 때까지 대기
    page.wait_for_selector(".todo-card", state="visible")


@pytest.mark.e2e
def test_add_todo_appears_in_list(page):
    """폼 제출 후 #todo-list에 카드가 등장해야 한다."""
    _add_todo(page)
    assert page.locator(".todo-card").count() == 1


@pytest.mark.e2e
def test_add_todo_shows_correct_title(page):
    """제출한 제목 텍스트가 카드에 표시되어야 한다."""
    _add_todo(page, title="중요한 할 일")
    assert page.locator(".todo-title").inner_text() == "중요한 할 일"


@pytest.mark.e2e
def test_add_todo_shows_priority_badge(page):
    """선택한 우선순위에 맞는 badge 클래스가 있어야 한다."""
    _add_todo(page, priority="high")
    assert page.locator(".badge-high").count() == 1


@pytest.mark.e2e
def test_add_todo_with_due_date(page):
    """마감일을 설정하면 .dday span이 카드에 표시되어야 한다."""
    _add_todo(page, due_date="2099-12-31")
    assert page.locator(".dday").is_visible()
    assert "D-" in page.locator(".dday").inner_text()


@pytest.mark.e2e
def test_add_todo_default_priority_is_medium(page):
    """우선순위를 변경하지 않으면 badge-medium 이어야 한다."""
    _add_todo(page)
    assert page.locator(".badge-medium").count() == 1


@pytest.mark.e2e
def test_form_clears_after_submit(page):
    """제출 후 제목과 설명 입력란이 비워져야 한다."""
    _add_todo(page)
    assert page.locator("#title").input_value() == ""
    assert page.locator("#description").input_value() == ""
