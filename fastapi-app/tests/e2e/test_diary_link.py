"""Diary ↔ Todo 연결 E2E 테스트 — v7.1.0 신규.

assertion은 모두 # TODO. 실제 UI 셀렉터/동작은 사용자가 확인 후 채울 것.
"""
import pytest


@pytest.mark.e2e
def test_diary_form_shows_todo_picker(page):
    """일기 작성 폼에 todo 첨부 선택 영역이 보이는지"""
    # TODO: 일기 작성 진입
    # TODO: assert page.locator("#linked-todos-picker") or 유사 셀렉터 visible
    pass


@pytest.mark.e2e
def test_diary_can_link_completed_todos(page):
    """일기에 그날 완료한 todo를 선택해서 연결할 수 있다"""
    # TODO: 오늘 완료된 todo 1개 미리 추가
    # TODO: 일기 작성 폼에서 첨부 후보로 그 todo가 보이는지 확인
    # TODO: 체크 → 일기 저장
    # TODO: 저장된 일기 상세에 연결 todo가 표시되는지 검증
    pass


@pytest.mark.e2e
def test_diary_detail_shows_linked_todos(page):
    """일기 상세 페이지에서 연결된 todo 목록이 노출됨"""
    # TODO: linked_todo_ids가 있는 일기 항목을 사전 세팅 (API 또는 fixture)
    # TODO: 일기 상세 화면 진입 → linked todos 영역 텍스트/카운트 검증
    pass


@pytest.mark.e2e
def test_diary_without_links_shows_empty_state(page):
    """linked_todo_ids가 빈 일기는 '연결된 todo 없음' 등 빈 상태 표시"""
    # TODO: linked_todo_ids=[] 일기 진입
    # TODO: 빈 상태 메시지 또는 영역 없음 검증
    pass
