import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from main import app, save_todos, load_todos, TodoItem, save_diary, load_diary, DiaryEntry

client = TestClient(app)

# ──────────────────────────────────────────────
# Fixture: 각 테스트 전후 상태 초기화
# ──────────────────────────────────────────────
@pytest.fixture(autouse=True)
def setup_and_teardown():
    save_todos([])
    save_diary([])
    yield
    save_todos([])
    save_diary([])


# ──────────────────────────────────────────────
# 데이터 모델링 테스트
# ──────────────────────────────────────────────
class TestDataModeling:
    def test_todo_item_default_values(self):
        """priority 기본값 medium, due_date 기본값 None 검증"""
        todo = TodoItem(id=1, title="Test", description="desc", completed=False)
        assert todo.priority == "medium"
        assert todo.due_date is None

    def test_todo_item_all_fields(self):
        """모든 필드를 명시적으로 지정한 경우 검증"""
        todo = TodoItem(
            id=2,
            title="Full",
            description="Full desc",
            completed=True,
            priority="high",
            due_date="2026-12-31"
        )
        assert todo.id == 2
        assert todo.title == "Full"
        assert todo.priority == "high"
        assert todo.due_date == "2026-12-31"
        assert todo.completed is True

    def test_todo_item_optional_due_date(self):
        """due_date는 선택 필드이므로 생략 가능"""
        todo = TodoItem(id=3, title="No Date", description="desc", completed=False)
        assert todo.due_date is None


# ──────────────────────────────────────────────
# 상태 관리 테스트
# ──────────────────────────────────────────────
class TestStateManagement:
    def test_save_and_load_todos(self):
        """save_todos / load_todos 함수가 정확히 동작하는지 검증"""
        todos = [
            {"id": 1, "title": "A", "description": "desc", "completed": False, "priority": "low", "due_date": None}
        ]
        save_todos(todos)
        loaded = load_todos()
        assert len(loaded) == 1
        assert loaded[0]["title"] == "A"

    def test_state_isolated_between_tests(self):
        """fixture로 인해 각 테스트가 독립적인 상태에서 시작하는지 검증"""
        todos = load_todos()
        assert todos == []

    def test_state_persists_within_test(self):
        """한 테스트 안에서 생성 후 조회 시 상태가 유지되는지 검증"""
        client.post("/todos", json={"id": 1, "title": "Persist", "description": "desc", "completed": False})
        response = client.get("/todos")
        assert len(response.json()) == 1


# ──────────────────────────────────────────────
# CRUD API 테스트
# ──────────────────────────────────────────────
class TestGetTodos:
    def test_get_todos_empty(self):
        """빈 상태에서 GET /todos → 빈 리스트 반환"""
        response = client.get("/todos")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_todos_with_items(self):
        """항목 저장 후 GET /todos → 항목 포함 리스트 반환"""
        todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
        save_todos([todo.model_dump()])
        response = client.get("/todos")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["title"] == "Test"

    def test_get_todos_multiple_items(self):
        """여러 항목 저장 후 전체 개수 검증"""
        todos = [
            TodoItem(id=i, title=f"Todo {i}", description="desc", completed=False).model_dump()
            for i in range(1, 4)
        ]
        save_todos(todos)
        response = client.get("/todos")
        assert response.status_code == 200
        assert len(response.json()) == 3


class TestCreateTodo:
    def test_create_todo(self):
        """POST /todos → 항목 생성 및 title 검증"""
        todo = {"id": 1, "title": "Test", "description": "Test description", "completed": False}
        response = client.post("/todos", json=todo)
        assert response.status_code == 200
        assert response.json()["title"] == "Test"

    def test_create_todo_with_all_fields(self):
        """모든 필드 포함한 항목 생성 검증"""
        todo = {
            "id": 2,
            "title": "Full Todo",
            "description": "Full description",
            "completed": False,
            "priority": "high",
            "due_date": "2026-12-31"
        }
        response = client.post("/todos", json=todo)
        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "high"
        assert data["due_date"] == "2026-12-31"

    def test_create_todo_default_priority(self):
        """priority 미입력 시 기본값 medium으로 생성"""
        todo = {"id": 3, "title": "Default Priority", "description": "desc", "completed": False}
        response = client.post("/todos", json=todo)
        assert response.status_code == 200
        assert response.json()["priority"] == "medium"


class TestUpdateTodo:
    def test_update_todo(self):
        """PUT /todos/{id} → 항목 수정 및 title 검증"""
        todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
        save_todos([todo.model_dump()])
        updated_todo = {"id": 1, "title": "Updated", "description": "Updated description", "completed": True}
        response = client.put("/todos/1", json=updated_todo)
        assert response.status_code == 200
        assert response.json()["title"] == "Updated"
        assert response.json()["completed"] is True

    def test_update_todo_not_found(self):
        """존재하지 않는 항목 수정 시 404 반환"""
        updated_todo = {"id": 999, "title": "Updated", "description": "Updated description", "completed": True}
        response = client.put("/todos/999", json=updated_todo)
        assert response.status_code == 404

    def test_update_todo_priority(self):
        """PUT /todos/{id} → priority 필드 수정 검증"""
        todo = TodoItem(id=1, title="Test", description="desc", completed=False, priority="low")
        save_todos([todo.model_dump()])
        updated = {"id": 1, "title": "Test", "description": "desc", "completed": False, "priority": "high"}
        response = client.put("/todos/1", json=updated)
        assert response.status_code == 200
        assert response.json()["priority"] == "high"


class TestDeleteTodo:
    def test_delete_todo(self):
        """DELETE /todos/{id} → 항목 삭제 후 메시지 검증"""
        todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
        save_todos([todo.model_dump()])
        response = client.delete("/todos/1")
        assert response.status_code == 200
        assert response.json()["message"] == "To-Do item deleted"

    def test_delete_todo_removes_from_list(self):
        """삭제 후 GET /todos에서 해당 항목이 없어지는지 검증"""
        todo = TodoItem(id=1, title="Test", description="desc", completed=False)
        save_todos([todo.model_dump()])
        client.delete("/todos/1")
        response = client.get("/todos")
        assert response.json() == []

    def test_delete_todo_not_found(self):
        """존재하지 않는 항목 삭제 시 404 반환"""
        response = client.delete("/todos/999")
        assert response.status_code == 404


# ──────────────────────────────────────────────
# 유효성 검사 테스트
# ──────────────────────────────────────────────
class TestValidation:
    def test_create_todo_missing_description(self):
        """필수 필드(description) 누락 시 422 반환"""
        todo = {"id": 1, "title": "Test"}
        response = client.post("/todos", json=todo)
        assert response.status_code == 422

    def test_create_todo_missing_title(self):
        """필수 필드(title) 누락 시 422 반환"""
        todo = {"id": 1, "description": "desc", "completed": False}
        response = client.post("/todos", json=todo)
        assert response.status_code == 422

    def test_create_todo_missing_completed(self):
        """필수 필드(completed) 누락 시 422 반환"""
        todo = {"id": 1, "title": "Test", "description": "desc"}
        response = client.post("/todos", json=todo)
        assert response.status_code == 422

    def test_create_todo_invalid_id_type(self):
        """id 타입이 int가 아닌 경우 422 반환"""
        todo = {"id": "not-an-int", "title": "Test", "description": "desc", "completed": False}
        response = client.post("/todos", json=todo)
        assert response.status_code == 422

    def test_update_todo_missing_fields(self):
        """PUT 요청 시 필수 필드 누락 → 422 반환"""
        todo = TodoItem(id=1, title="Test", description="desc", completed=False)
        save_todos([todo.model_dump()])
        response = client.put("/todos/1", json={"title": "Only Title"})
        assert response.status_code == 422


# ──────────────────────────────────────────────
# 추가 기능 테스트 (검색 / 토글 / 헬스체크)
# ──────────────────────────────────────────────
class TestSearchTodo:
    def test_search_todos_found(self):
        """키워드 포함 항목 검색 시 결과 반환"""
        todos = [
            TodoItem(id=1, title="FastAPI 공부", description="desc", completed=False).model_dump(),
            TodoItem(id=2, title="운동하기", description="desc", completed=False).model_dump(),
        ]
        save_todos(todos)
        response = client.get("/todos/search?keyword=FastAPI")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["title"] == "FastAPI 공부"

    def test_search_todos_not_found(self):
        """키워드 미포함 시 빈 리스트 반환"""
        todo = TodoItem(id=1, title="운동하기", description="desc", completed=False)
        save_todos([todo.model_dump()])
        response = client.get("/todos/search?keyword=FastAPI")
        assert response.status_code == 200
        assert response.json() == []

    def test_search_todos_case_insensitive(self):
        """검색은 대소문자 구분 없이 동작"""
        todo = TodoItem(id=1, title="fastapi study", description="desc", completed=False)
        save_todos([todo.model_dump()])
        response = client.get("/todos/search?keyword=FASTAPI")
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestToggleTodo:
    def test_toggle_todo_completed(self):
        """PATCH /todos/{id}/toggle → completed 상태 반전 검증"""
        todo = TodoItem(id=1, title="Test", description="desc", completed=False)
        save_todos([todo.model_dump()])
        response = client.patch("/todos/1/toggle")
        assert response.status_code == 200
        assert response.json()["completed"] is True

    def test_toggle_todo_twice(self):
        """두 번 토글 시 원래 상태로 돌아오는지 검증"""
        todo = TodoItem(id=1, title="Test", description="desc", completed=False)
        save_todos([todo.model_dump()])
        client.patch("/todos/1/toggle")
        response = client.patch("/todos/1/toggle")
        assert response.json()["completed"] is False

    def test_toggle_todo_not_found(self):
        """존재하지 않는 항목 토글 시 404 반환"""
        response = client.patch("/todos/999/toggle")
        assert response.status_code == 404


# ──────────────────────────────────────────────
# 필터링 테스트 (v4.0.0 신규)
# ──────────────────────────────────────────────
class TestFilterTodos:
    def test_filter_by_priority(self):
        """priority=high 필터 → high 항목만 반환"""
        todos = [
            TodoItem(id=1, title="High Task", description="desc", completed=False, priority="high").model_dump(),
            TodoItem(id=2, title="Low Task",  description="desc", completed=False, priority="low").model_dump(),
        ]
        save_todos(todos)
        response = client.get("/todos?priority=high")
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]["priority"] == "high"

    def test_filter_by_completed(self):
        """completed=true 필터 → 완료 항목만 반환"""
        todos = [
            TodoItem(id=1, title="Done",    description="desc", completed=True).model_dump(),
            TodoItem(id=2, title="Pending", description="desc", completed=False).model_dump(),
        ]
        save_todos(todos)
        response = client.get("/todos?completed=true")
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]["completed"] is True

    def test_filter_combined(self):
        """priority=high & completed=false 복합 필터"""
        todos = [
            TodoItem(id=1, title="High Pending", description="desc", completed=False, priority="high").model_dump(),
            TodoItem(id=2, title="High Done",    description="desc", completed=True,  priority="high").model_dump(),
            TodoItem(id=3, title="Low Pending",  description="desc", completed=False, priority="low").model_dump(),
        ]
        save_todos(todos)
        response = client.get("/todos?priority=high&completed=false")
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]["title"] == "High Pending"

    def test_filter_no_match(self):
        """필터 조건에 맞는 항목 없을 시 빈 리스트 반환"""
        todo = TodoItem(id=1, title="Low Task", description="desc", completed=False, priority="low")
        save_todos([todo.model_dump()])
        response = client.get("/todos?priority=high")
        assert response.status_code == 200
        assert response.json() == []


# ──────────────────────────────────────────────
# 통계 테스트 (v4.0.0 신규)
# ──────────────────────────────────────────────
class TestStatsTodo:
    def test_stats_empty(self):
        """빈 상태 통계 → 모두 0, completion_rate 0.0"""
        response = client.get("/todos/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["completed"] == 0
        assert data["pending"] == 0
        assert data["completion_rate"] == pytest.approx(0.0)

    def test_stats_with_todos(self):
        """항목 추가 후 통계 수치 정확성 검증"""
        todos = [
            TodoItem(id=1, title="A", description="desc", completed=True,  priority="high").model_dump(),
            TodoItem(id=2, title="B", description="desc", completed=False, priority="high").model_dump(),
            TodoItem(id=3, title="C", description="desc", completed=False, priority="low").model_dump(),
        ]
        save_todos(todos)
        response = client.get("/todos/stats")
        data = response.json()
        assert data["total"] == 3
        assert data["completed"] == 1
        assert data["pending"] == 2
        assert data["completion_rate"] == pytest.approx(33.3)

    def test_stats_by_priority(self):
        """priority별 카운트 정확성 검증"""
        todos = [
            TodoItem(id=1, title="A", description="desc", completed=False, priority="high").model_dump(),
            TodoItem(id=2, title="B", description="desc", completed=False, priority="high").model_dump(),
            TodoItem(id=3, title="C", description="desc", completed=False, priority="medium").model_dump(),
            TodoItem(id=4, title="D", description="desc", completed=False, priority="low").model_dump(),
        ]
        save_todos(todos)
        response = client.get("/todos/stats")
        data = response.json()
        assert data["by_priority"]["high"] == 2
        assert data["by_priority"]["medium"] == 1
        assert data["by_priority"]["low"] == 1

    def test_stats_completion_rate_100(self):
        """모두 완료 시 completion_rate 100.0"""
        todos = [
            TodoItem(id=1, title="A", description="desc", completed=True).model_dump(),
            TodoItem(id=2, title="B", description="desc", completed=True).model_dump(),
        ]
        save_todos(todos)
        response = client.get("/todos/stats")
        assert response.json()["completion_rate"] == pytest.approx(100.0)


class TestHealthCheck:
    def test_health_check_empty(self):
        """빈 상태에서 /health → 정상 상태 및 카운트 검증"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "7.0.0"
        assert data["total_todos"] == 0
        assert data["completed"] == 0
        assert data["pending"] == 0

    def test_health_check_with_todos(self):
        """항목 추가 후 /health → 카운트 정확성 검증"""
        todos = [
            TodoItem(id=1, title="Done", description="desc", completed=True).model_dump(),
            TodoItem(id=2, title="Pending", description="desc", completed=False).model_dump(),
        ]
        save_todos(todos)
        response = client.get("/health")
        data = response.json()
        assert data["total_todos"] == 2
        assert data["completed"] == 1
        assert data["pending"] == 1


# ──────────────────────────────────────────────
# 카테고리 테스트 (v6.0.0 신규)
# ──────────────────────────────────────────────
class TestCategory:
    def test_todo_item_default_category(self):
        """category 기본값은 'other'"""
        todo = TodoItem(id=1, title="Test", description="desc", completed=False)
        assert todo.category == "other"

    def test_create_todo_with_category(self):
        """POST /todos → category 필드가 정상 저장"""
        todo = {"id": 1, "title": "Work Task", "description": "desc", "completed": False, "category": "work"}
        response = client.post("/todos", json=todo)
        assert response.status_code == 200
        assert response.json()["category"] == "work"

    def test_filter_by_category(self):
        """category=work 필터 → work 항목만 반환"""
        todos = [
            TodoItem(id=1, title="A", description="desc", completed=False, category="work").model_dump(),
            TodoItem(id=2, title="B", description="desc", completed=False, category="study").model_dump(),
            TodoItem(id=3, title="C", description="desc", completed=False, category="work").model_dump(),
        ]
        save_todos(todos)
        response = client.get("/todos?category=work")
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 2
        assert all(t["category"] == "work" for t in result)

    def test_filter_combined_priority_and_category(self):
        """priority=high & category=study 복합 필터"""
        todos = [
            TodoItem(id=1, title="A", description="desc", completed=False, priority="high", category="study").model_dump(),
            TodoItem(id=2, title="B", description="desc", completed=False, priority="high", category="work").model_dump(),
            TodoItem(id=3, title="C", description="desc", completed=False, priority="low",  category="study").model_dump(),
        ]
        save_todos(todos)
        response = client.get("/todos?priority=high&category=study")
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]["title"] == "A"

    def test_update_todo_category(self):
        """PUT /todos/{id} → category 필드 수정"""
        todo = TodoItem(id=1, title="Test", description="desc", completed=False, category="other")
        save_todos([todo.model_dump()])
        updated = {"id": 1, "title": "Test", "description": "desc", "completed": False, "category": "exercise"}
        response = client.put("/todos/1", json=updated)
        assert response.status_code == 200
        assert response.json()["category"] == "exercise"

    def test_stats_by_category(self):
        """category별 카운트 정확성 검증"""
        todos = [
            TodoItem(id=1, title="A", description="desc", completed=False, category="work").model_dump(),
            TodoItem(id=2, title="B", description="desc", completed=False, category="work").model_dump(),
            TodoItem(id=3, title="C", description="desc", completed=False, category="study").model_dump(),
            TodoItem(id=4, title="D", description="desc", completed=False, category="hobby").model_dump(),
        ]
        save_todos(todos)
        response = client.get("/todos/stats")
        data = response.json()
        assert data["by_category"]["work"]     == 2
        assert data["by_category"]["study"]    == 1
        assert data["by_category"]["hobby"]    == 1
        assert data["by_category"]["exercise"] == 0
        assert data["by_category"]["other"]    == 0

    def test_filter_by_category_other_for_legacy_data(self):
        """category 필드가 없는 기존 데이터는 'other'로 필터링되어야 함"""
        legacy_todos = [
            {"id": 1, "title": "Legacy", "description": "desc", "completed": False, "priority": "medium"},
        ]
        save_todos(legacy_todos)
        response = client.get("/todos?category=other")
        assert response.status_code == 200
        assert len(response.json()) == 1


# ──────────────────────────────────────────────
# 메모(notes) 필드 테스트 (v6.2.0 신규)
# ──────────────────────────────────────────────
class TestNotes:
    def test_todo_item_default_notes(self):
        """notes 기본값은 None"""
        todo = TodoItem(id=1, title="Test", description="desc", completed=False)
        assert todo.notes is None

    def test_create_todo_with_notes(self):
        """POST /todos → notes 필드가 정상 저장"""
        todo = {"id": 1, "title": "T", "description": "d", "completed": False, "notes": "비밀 메모"}
        response = client.post("/todos", json=todo)
        assert response.status_code == 200
        assert response.json()["notes"] == "비밀 메모"

    def test_create_todo_without_notes(self):
        """POST /todos → notes 미지정 시 None 으로 저장"""
        todo = {"id": 2, "title": "T", "description": "d", "completed": False}
        response = client.post("/todos", json=todo)
        assert response.status_code == 200
        assert response.json()["notes"] is None

    def test_update_todo_notes(self):
        """PUT /todos/{id} → notes 필드 수정"""
        todo = TodoItem(id=1, title="T", description="d", completed=False, notes="원본")
        save_todos([todo.model_dump()])
        updated = {"id": 1, "title": "T", "description": "d", "completed": False, "notes": "수정됨"}
        response = client.put("/todos/1", json=updated)
        assert response.status_code == 200
        assert response.json()["notes"] == "수정됨"

    def test_update_todo_clear_notes(self):
        """PUT /todos/{id} → notes 를 None 으로 비우기"""
        todo = TodoItem(id=1, title="T", description="d", completed=False, notes="삭제될 메모")
        save_todos([todo.model_dump()])
        updated = {"id": 1, "title": "T", "description": "d", "completed": False, "notes": None}
        response = client.put("/todos/1", json=updated)
        assert response.status_code == 200
        assert response.json()["notes"] is None

    def test_get_todos_returns_notes(self):
        """GET /todos → 응답에 notes 필드 포함"""
        todo = TodoItem(id=1, title="T", description="d", completed=False, notes="응답 확인용")
        save_todos([todo.model_dump()])
        response = client.get("/todos")
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert "notes" in result[0]
        assert result[0]["notes"] == "응답 확인용"

    def test_legacy_data_without_notes(self):
        """notes 필드가 없는 기존 데이터 호환성 (None 으로 처리)"""
        legacy = [{"id": 1, "title": "L", "description": "d", "completed": False, "priority": "medium"}]
        save_todos(legacy)
        response = client.get("/todos")
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]["notes"] is None


# ──────────────────────────────────────────────
# 일기장(Diary) API 테스트 (v6.3.0 신규)
# ──────────────────────────────────────────────
class TestDiaryModel:
    def test_diary_entry_default_mood(self):
        """mood 기본값은 'happy'"""
        entry = DiaryEntry(id=1, date="2026-05-15", title="오늘", content="좋은 하루")
        assert entry.mood == "happy"

    def test_diary_entry_all_fields(self):
        """모든 필드 명시 시 정확히 저장"""
        entry = DiaryEntry(id=2, date="2026-05-14", title="제목", content="내용", mood="love")
        assert entry.id == 2
        assert entry.date == "2026-05-14"
        assert entry.title == "제목"
        assert entry.content == "내용"
        assert entry.mood == "love"


class TestDiaryStateManagement:
    def test_save_and_load_diary(self):
        """save_diary / load_diary 함수가 정확히 동작"""
        entries = [
            {"id": 1, "date": "2026-05-15", "title": "A", "content": "내용", "mood": "happy"}
        ]
        save_diary(entries)
        loaded = load_diary()
        assert len(loaded) == 1
        assert loaded[0]["title"] == "A"

    def test_diary_isolated_between_tests(self):
        """fixture로 인해 각 테스트가 빈 일기 상태로 시작"""
        assert load_diary() == []


class TestDiaryCreate:
    def test_create_diary_entry(self):
        """POST /diary → 일기 항목 생성"""
        body = {"id": 1, "date": "2026-05-15", "title": "테스트", "content": "오늘은 좋은 날", "mood": "happy"}
        response = client.post("/diary", json=body)
        assert response.status_code == 200
        assert response.json()["title"] == "테스트"
        assert response.json()["mood"] == "happy"

    def test_create_diary_default_mood(self):
        """mood 미지정 시 기본값 'happy'"""
        body = {"id": 2, "date": "2026-05-15", "title": "기본", "content": "내용"}
        response = client.post("/diary", json=body)
        assert response.status_code == 200
        assert response.json()["mood"] == "happy"

    def test_create_diary_missing_content(self):
        """필수 필드 content 누락 시 422"""
        body = {"id": 3, "date": "2026-05-15", "title": "X"}
        response = client.post("/diary", json=body)
        assert response.status_code == 422

    def test_create_diary_missing_date(self):
        """필수 필드 date 누락 시 422"""
        body = {"id": 4, "title": "X", "content": "x"}
        response = client.post("/diary", json=body)
        assert response.status_code == 422


class TestDiaryRead:
    def test_get_diary_empty(self):
        """빈 상태 GET /diary → 빈 리스트"""
        response = client.get("/diary")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_diary_sorted_by_date_desc(self):
        """GET /diary → 날짜 내림차순 정렬"""
        save_diary([
            {"id": 1, "date": "2026-05-10", "title": "old",   "content": "x", "mood": "happy"},
            {"id": 2, "date": "2026-05-15", "title": "new",   "content": "x", "mood": "happy"},
            {"id": 3, "date": "2026-05-12", "title": "mid",   "content": "x", "mood": "happy"},
        ])
        response = client.get("/diary")
        result = response.json()
        assert [e["title"] for e in result] == ["new", "mid", "old"]

    def test_filter_by_mood(self):
        """GET /diary?mood=love → love 항목만 반환"""
        save_diary([
            {"id": 1, "date": "2026-05-15", "title": "A", "content": "x", "mood": "love"},
            {"id": 2, "date": "2026-05-14", "title": "B", "content": "x", "mood": "sad"},
            {"id": 3, "date": "2026-05-13", "title": "C", "content": "x", "mood": "love"},
        ])
        response = client.get("/diary?mood=love")
        result = response.json()
        assert len(result) == 2
        assert all(e["mood"] == "love" for e in result)

    def test_get_by_date(self):
        """GET /diary/by-date/{date} → 특정 날짜 항목만"""
        save_diary([
            {"id": 1, "date": "2026-05-15", "title": "Today A", "content": "x", "mood": "happy"},
            {"id": 2, "date": "2026-05-14", "title": "Yesterday", "content": "x", "mood": "happy"},
            {"id": 3, "date": "2026-05-15", "title": "Today B", "content": "x", "mood": "sad"},
        ])
        response = client.get("/diary/by-date/2026-05-15")
        result = response.json()
        assert len(result) == 2
        assert {e["title"] for e in result} == {"Today A", "Today B"}


class TestDiaryUpdate:
    def test_update_diary(self):
        """PUT /diary/{id} → 항목 수정"""
        save_diary([{"id": 1, "date": "2026-05-15", "title": "원본", "content": "old", "mood": "happy"}])
        body = {"id": 1, "date": "2026-05-15", "title": "수정됨", "content": "new", "mood": "love"}
        response = client.put("/diary/1", json=body)
        assert response.status_code == 200
        assert response.json()["title"] == "수정됨"
        assert response.json()["mood"] == "love"

    def test_update_diary_not_found(self):
        """존재하지 않는 id 수정 시 404"""
        body = {"id": 999, "date": "2026-05-15", "title": "x", "content": "x", "mood": "happy"}
        response = client.put("/diary/999", json=body)
        assert response.status_code == 404


class TestDiaryDelete:
    def test_delete_diary(self):
        """DELETE /diary/{id} → 항목 삭제"""
        save_diary([{"id": 1, "date": "2026-05-15", "title": "X", "content": "x", "mood": "happy"}])
        response = client.delete("/diary/1")
        assert response.status_code == 200
        assert response.json()["message"] == "Diary entry deleted"
        assert load_diary() == []

    def test_delete_diary_not_found(self):
        """존재하지 않는 id 삭제 시 404"""
        response = client.delete("/diary/999")
        assert response.status_code == 404


class TestDiaryStats:
    def test_diary_stats_empty(self):
        """빈 상태 /diary/stats → total 0, 모든 mood 0"""
        response = client.get("/diary/stats")
        data = response.json()
        assert data["total"] == 0
        assert data["by_mood"]["happy"] == 0
        assert data["by_mood"]["love"] == 0

    def test_diary_stats_by_mood(self):
        """mood별 카운트 정확성"""
        save_diary([
            {"id": 1, "date": "2026-05-15", "title": "A", "content": "x", "mood": "happy"},
            {"id": 2, "date": "2026-05-14", "title": "B", "content": "x", "mood": "happy"},
            {"id": 3, "date": "2026-05-13", "title": "C", "content": "x", "mood": "love"},
            {"id": 4, "date": "2026-05-12", "title": "D", "content": "x", "mood": "sad"},
        ])
        response = client.get("/diary/stats")
        data = response.json()
        assert data["total"] == 4
        assert data["by_mood"]["happy"] == 2
        assert data["by_mood"]["love"]  == 1
        assert data["by_mood"]["sad"]   == 1


class TestRootAndUtils:
    def test_root_returns_html(self):
        """GET / → HTML 응답 반환 검증"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_load_todos_returns_empty_when_no_file(self):
        """todo.json 파일이 없을 때 load_todos → 빈 리스트 반환"""
        if os.path.exists("todo.json"):
            os.remove("todo.json")
        result = load_todos()
        assert result == []
