"""메모(notes) 필드 E2E 테스트 (v6.2.0 신규)."""
import pytest


@pytest.mark.e2e
def test_notes_textarea_visible_in_form(page):
    """폼에 #notes textarea 가 보여야 한다."""
    # TODO: page.locator("#notes").is_visible() 패턴
    pass


@pytest.mark.e2e
def test_notes_textarea_has_placeholder(page):
    """#notes textarea 에 안내 placeholder 가 있어야 한다."""
    # TODO: placeholder 속성 검증
    pass


@pytest.mark.e2e
def test_add_todo_with_notes(page):
    """notes 를 입력하고 제출하면 카드에 메모가 표시되어야 한다."""
    # TODO: page.fill("#notes", ...) → 제출 → 카드에 노출 확인
    pass


@pytest.mark.e2e
def test_add_todo_without_notes(page):
    """notes 비워둔 채 제출해도 정상 등록되어야 한다."""
    # TODO: notes 입력 없이 제출 → 카드 등장 + 메모 영역 비어있음
    pass


@pytest.mark.e2e
def test_notes_field_clears_after_submit(page):
    """제출 후 #notes textarea 가 비워져야 한다."""
    # TODO: 제출 후 input_value() == "" 확인
    pass
