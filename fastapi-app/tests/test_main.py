import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from main import app, save_todos, load_todos, TodoItem

client = TestClient(app)

# ──────────────────────────────────────────────
# Fixture: 각 테스트 전후 상태 초기화
# ──────────────────────────────────────────────
@pytest.fixture(autouse=True)
def setup_and_teardown():
    save_todos([])
    yield
    save_todos([])


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
        assert data["version"] == "5.0.0"
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
