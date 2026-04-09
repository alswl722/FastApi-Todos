"""할 일 수정(모달) E2E 테스트."""
import pytest


def _add_todo(page, title="수정 테스트", priority="medium"):
    page.fill("#title", title)
    page.fill("#description", "원래 설명")
    page.select_option("#priority", priority)
    page.click("button[type='submit']")
    page.wait_for_selector(".todo-card", state="visible")


@pytest.mark.e2e
def test_edit_button_opens_modal(page):
    """'수정' 버튼 클릭 시 편집 모달이 표시되어야 한다."""
    _add_todo(page)
    page.locator("button:has-text('수정')").first.click()
    page.wait_for_selector("#edit-modal", state="visible")
    assert page.locator("#edit-modal").is_visible()


@pytest.mark.e2e
def test_edit_modal_prefills_values(page):
    """모달 입력값이 기존 todo 데이터로 채워져야 한다."""
    _add_todo(page, title="원래 제목")
    page.locator("button:has-text('수정')").first.click()
    page.wait_for_selector("#edit-modal", state="visible")
    assert page.locator("#edit-title").input_value() == "원래 제목"
    assert page.locator("#edit-description").input_value() == "원래 설명"


@pytest.mark.e2e
def test_edit_save_updates_card_title(page):
    """제목 수정 후 저장하면 카드의 제목이 변경되어야 한다."""
    _add_todo(page, title="원래 제목")
    page.locator("button:has-text('수정')").first.click()
    page.wait_for_selector("#edit-modal", state="visible")
    page.fill("#edit-title", "수정된 제목")
    page.locator("button:has-text('저장')").click()
    page.wait_for_function(
        "document.querySelector('.todo-title')?.textContent === '수정된 제목'"
    )
    assert page.locator(".todo-title").inner_text() == "수정된 제목"


@pytest.mark.e2e
def test_edit_save_updates_priority_badge(page):
    """우선순위 변경 후 저장하면 badge 클래스가 변경되어야 한다."""
    _add_todo(page, priority="low")
    assert page.locator(".badge-low").count() == 1
    page.locator("button:has-text('수정')").first.click()
    page.wait_for_selector("#edit-modal", state="visible")
    page.select_option("#edit-priority", "high")
    page.locator("button:has-text('저장')").click()
    page.wait_for_selector(".badge-high", state="visible")
    assert page.locator(".badge-high").count() == 1


@pytest.mark.e2e
def test_edit_cancel_closes_modal(page):
    """'취소' 클릭 시 모달이 닫혀야 한다."""
    _add_todo(page)
    page.locator("button:has-text('수정')").first.click()
    page.wait_for_selector("#edit-modal", state="visible")
    page.locator("button:has-text('취소')").click()
    page.wait_for_selector("#edit-modal", state="hidden")
    assert not page.locator("#edit-modal").is_visible()


@pytest.mark.e2e
def test_edit_modal_closes_on_backdrop_click(page):
    """모달 오버레이(배경) 클릭 시 모달이 닫혀야 한다."""
    _add_todo(page)
    page.locator("button:has-text('수정')").first.click()
    page.wait_for_selector("#edit-modal", state="visible")
    # 모달 박스 밖의 오버레이 영역 클릭
    page.locator("#edit-modal").click(position={"x": 5, "y": 5})
    page.wait_for_selector("#edit-modal", state="hidden")
    assert not page.locator("#edit-modal").is_visible()
