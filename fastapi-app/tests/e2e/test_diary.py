"""일기장(Diary) 기능 E2E 테스트 (v6.3.0 신규)."""
import json
import os
import pytest

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DIARY_FILE = os.path.join(APP_DIR, "diary.json")


@pytest.fixture(autouse=True)
def clean_diary():
    """매 테스트 전후 diary.json 을 빈 배열로 초기화."""
    with open(DIARY_FILE, "w") as f:
        json.dump([], f)
    yield
    with open(DIARY_FILE, "w") as f:
        json.dump([], f)


def _switch_to_diary_tab(page):
    """일기장 탭으로 전환하는 헬퍼."""
    page.click("#tab-diary")
    page.wait_for_selector("#diary-section.active", state="visible")


def _add_diary_entry(page, title="오늘의 일기", content="오늘 있었던 일", mood=None, date=None):
    """일기장 폼에 데이터를 입력하고 제출하는 헬퍼."""
    _switch_to_diary_tab(page)
    if date:
        page.fill("#diary-date", date)
    page.fill("#diary-title", title)
    page.fill("#diary-content", content)
    if mood:
        page.select_option("#diary-mood", mood)
    page.click("#diary-form button[type='submit']")
    page.wait_for_selector(".diary-card", state="visible")


@pytest.mark.e2e
def test_switch_to_diary_tab(page):
    """일기장 탭 버튼 클릭 시 #diary-section이 활성화되어야 한다."""
    _switch_to_diary_tab(page)
    assert "active" in (page.locator("#diary-section").get_attribute("class") or "")
    assert page.locator("#tab-diary").get_attribute("class").find("active") != -1


@pytest.mark.e2e
def test_add_diary_entry_appears_in_list(page):
    """폼 제출 후 .diary-card가 목록에 등장해야 한다."""
    _add_diary_entry(page)
    assert page.locator(".diary-card").count() == 1


@pytest.mark.e2e
def test_add_diary_shows_correct_title(page):
    """제출한 제목이 .diary-title에 표시되어야 한다."""
    _add_diary_entry(page, title="특별한 제목")
    assert page.locator(".diary-title").inner_text() == "특별한 제목"


@pytest.mark.e2e
def test_add_diary_default_mood_is_happy(page):
    """mood를 변경하지 않으면 .mood-happy 뱃지가 생성되어야 한다."""
    _add_diary_entry(page)
    assert page.locator(".mood-happy").count() == 1


@pytest.mark.e2e
def test_add_diary_with_mood_love(page):
    """mood='love' 선택 시 .mood-love 뱃지가 생성되어야 한다."""
    _add_diary_entry(page, mood="love")
    assert page.locator(".mood-love").count() == 1


@pytest.mark.e2e
def test_diary_mood_filter_works(page):
    """무드 필터 버튼 클릭 시 해당 mood 항목만 표시되어야 한다."""
    _add_diary_entry(page, title="행복한 날", mood="happy")
    _add_diary_entry(page, title="사랑한 날", mood="love")
    # 사랑 필터 클릭
    page.click(".mf-btn:has-text('사랑')")
    page.wait_for_function("document.querySelectorAll('.diary-card').length === 1")
    assert page.locator(".diary-card").count() == 1
    assert page.locator(".diary-title").inner_text() == "사랑한 날"


@pytest.mark.e2e
def test_diary_delete_removes_card(page):
    """삭제 버튼 클릭(confirm 승인) 후 카드가 사라져야 한다."""
    _add_diary_entry(page)
    # window.confirm 자동 승인
    page.on("dialog", lambda dialog: dialog.accept())
    page.click(".diary-card .btn-danger")
    page.wait_for_function("document.querySelectorAll('.diary-card').length === 0")
    assert page.locator(".diary-card").count() == 0


@pytest.mark.e2e
def test_diary_form_clears_after_submit(page):
    """제출 후 제목/내용 입력란이 비워져야 한다."""
    _add_diary_entry(page, title="비워질 제목", content="비워질 내용")
    assert page.locator("#diary-title").input_value() == ""
    assert page.locator("#diary-content").input_value() == ""
