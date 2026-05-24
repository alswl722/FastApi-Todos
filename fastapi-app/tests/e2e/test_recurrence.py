"""반복 todo (recurrence) E2E 테스트 — v7.1.0 신규.

assertion은 모두 # TODO. 실제 UI 셀렉터/동작은 사용자가 확인 후 채울 것.
"""
import pytest


@pytest.mark.e2e
def test_recurrence_select_visible_in_form(page):
    """폼에 recurrence 선택 요소(select 또는 radio)가 노출되는지"""
    # TODO: page.goto(BASE_URL) 등 진입
    # TODO: assert page.locator("#recurrence").is_visible()
    pass


@pytest.mark.e2e
def test_recurrence_daily_creates_repeating_todo(page):
    """recurrence=daily로 todo 추가 → 카드에 반복 표시 노출"""
    # TODO: 폼에서 recurrence="daily" 선택 + due_date 지정 후 제출
    # TODO: 생성된 카드에 "매일" 또는 .recurrence-badge 등 visible
    pass


@pytest.mark.e2e
def test_completing_recurring_todo_spawns_next(page):
    """반복 todo 완료시 다음 회차 카드가 자동 생성되어 리스트에 추가됨"""
    # TODO: recurring todo 1개 추가 → 완료 버튼 클릭
    # TODO: page.wait_for_selector(".todo-card:nth-child(2)") 또는 카드 수 == 2 검증
    # TODO: 새 카드의 due_date 텍스트가 다음날인지 확인
    pass


@pytest.mark.e2e
def test_completed_at_displayed_on_card(page):
    """완료한 todo 카드에 완료 날짜가 표시됨"""
    # TODO: todo 추가 → 완료 토글 → .completed-at 등 셀렉터 텍스트 확인
    pass
