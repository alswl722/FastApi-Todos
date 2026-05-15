"""메모(notes) 필드 E2E 테스트 (v6.2.0 신규)."""
import pytest


def _add_todo_with_notes(page, title="할 일", description="설명", notes=None):
    """폼 입력 헬퍼 — notes 선택 입력."""
    page.fill("#title", title)
    page.fill("#description", description)
    if notes is not None:
        page.fill("#notes", notes)
    page.click("#todo-form button[type='submit']")
    page.wait_for_selector(".todo-card", state="visible")


@pytest.mark.e2e
def test_notes_textarea_visible_in_form(page):
    """폼에 #notes textarea 가 보여야 한다."""
    assert page.locator("#notes").is_visible()


@pytest.mark.e2e
def test_notes_textarea_has_placeholder(page):
    """#notes textarea 에 안내 placeholder 가 있어야 한다."""
    placeholder = page.locator("#notes").get_attribute("placeholder")
    assert placeholder is not None
    assert "메모" in placeholder


@pytest.mark.e2e
def test_add_todo_with_notes(page):
    """notes 를 입력하고 제출하면 카드에 메모가 표시되어야 한다."""
    _add_todo_with_notes(page, notes="비밀 메모입니다")
    notes_locator = page.locator(".todo-notes")
    assert notes_locator.count() == 1
    assert "비밀 메모입니다" in notes_locator.inner_text()


@pytest.mark.e2e
def test_add_todo_without_notes(page):
    """notes 비워둔 채 제출해도 정상 등록되어야 한다."""
    _add_todo_with_notes(page)
    assert page.locator(".todo-card").count() == 1
    # 메모 없을 때는 .todo-notes 요소 자체가 렌더링되지 않음
    assert page.locator(".todo-notes").count() == 0


@pytest.mark.e2e
def test_notes_field_clears_after_submit(page):
    """제출 후 #notes textarea 가 비워져야 한다."""
    _add_todo_with_notes(page, notes="제출 후 비워질 메모")
    assert page.locator("#notes").input_value() == ""
