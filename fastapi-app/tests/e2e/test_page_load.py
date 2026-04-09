"""페이지 로드 및 기본 UI 요소 존재 여부 확인."""
import pytest


@pytest.mark.e2e
def test_page_title_visible(page):
    """h1 제목이 앱 이름을 포함해야 한다."""
    heading = page.locator("h1")
    assert heading.is_visible()
    assert "To-Do" in heading.inner_text()


@pytest.mark.e2e
def test_stats_dashboard_visible(page):
    """통계 대시보드 섹션이 렌더링되어야 한다."""
    assert page.locator(".stats-dashboard").is_visible()
    assert page.locator("#stat-total").is_visible()
    assert page.locator("#stat-completed").is_visible()
    assert page.locator("#stat-pending").is_visible()


@pytest.mark.e2e
def test_form_inputs_present(page):
    """입력 폼의 모든 필드가 존재해야 한다."""
    assert page.locator("#title").is_visible()
    assert page.locator("#description").is_visible()
    assert page.locator("#priority").is_visible()
    assert page.locator("#due_date").is_visible()
    assert page.locator("#todo-form button[type='submit']").is_visible()


@pytest.mark.e2e
def test_filter_buttons_visible(page):
    """상태 필터 버튼(전체/미완료/완료)이 모두 표시되어야 한다."""
    buttons = page.locator(".filter-btn")
    assert buttons.count() == 3


@pytest.mark.e2e
def test_priority_filter_buttons_visible(page):
    """우선순위 필터 버튼(전체/높음/보통/낮음)이 모두 표시되어야 한다."""
    buttons = page.locator(".pf-btn")
    assert buttons.count() == 4


@pytest.mark.e2e
def test_search_input_visible(page):
    """검색 입력창이 표시되어야 한다."""
    assert page.locator("#search-input").is_visible()
