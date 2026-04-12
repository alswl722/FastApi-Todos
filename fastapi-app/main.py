from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import json
import os

app = FastAPI(
    title="Minji's Todo List",
    description="VDI 배포 과제용 업그레이드 버전",
    version="5.0.0"
)

# To-Do 항목 모델
class TodoItem(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    priority: str = "medium"       # low / medium / high
    due_date: Optional[str] = None # YYYY-MM-DD

# JSON 파일 경로
TODO_FILE = "todo.json"

# JSON 파일에서 To-Do 항목 로드
def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r") as file:
            return json.load(file)
    return []

# JSON 파일에 To-Do 항목 저장
def save_todos(todos):
    with open(TODO_FILE, "w") as file:
        json.dump(todos, file, indent=4, ensure_ascii=False)

# To-Do 목록 조회 (priority / completed 필터 지원)
@app.get("/todos", response_model=list[TodoItem])
def get_todos(
    priority: Optional[str] = Query(None, description="low / medium / high"),
    completed: Optional[bool] = Query(None, description="true / false"),
):
    todos = load_todos()
    if priority is not None:
        todos = [t for t in todos if t["priority"] == priority]
    if completed is not None:
        todos = [t for t in todos if t["completed"] == completed]
    return todos

# 특정 키워드가 포함된 할 일 검색
@app.get("/todos/search")
def search_todos(keyword: str):
    todos = load_todos()
    results = [todo for todo in todos if keyword.lower() in todo["title"].lower()]
    return results

# To-Do 통계 조회
@app.get("/todos/stats")
def get_stats():
    todos = load_todos()
    total = len(todos)
    completed = sum(1 for t in todos if t["completed"])
    return {
        "total": total,
        "completed": completed,
        "pending": total - completed,
        "completion_rate": round(completed / total * 100, 1) if total > 0 else 0.0,
        "by_priority": {
            "high":   sum(1 for t in todos if t["priority"] == "high"),
            "medium": sum(1 for t in todos if t["priority"] == "medium"),
            "low":    sum(1 for t in todos if t["priority"] == "low"),
        },
    }

# 신규 To-Do 항목 추가
@app.post("/todos", response_model=TodoItem)
def create_todo(todo: TodoItem):
    todos = load_todos()
    todos.append(todo.model_dump())
    save_todos(todos)
    return todo

# To-Do 항목 수정
@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, updated_todo: TodoItem):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo.update(updated_todo.model_dump())
            save_todos(todos)
            return updated_todo
    raise HTTPException(status_code=404, detail="To-Do item not found")

# 완료 상태만 토글
@app.patch("/todos/{todo_id}/toggle")
def toggle_todo(todo_id: int):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo["completed"] = not todo["completed"]
            save_todos(todos)
            return todo
    raise HTTPException(status_code=404, detail="To-Do item not found")

# To-Do 항목 삭제
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    todos = load_todos()
    new_todos = [todo for todo in todos if todo["id"] != todo_id]
    if len(new_todos) == len(todos):
        raise HTTPException(status_code=404, detail="To-Do item not found")
    save_todos(new_todos)
    return {"message": "To-Do item deleted"}

# 서버 상태 확인
@app.get("/health")
def health_check():
    todos = load_todos()
    return {
        "status": "ok",
        "version": "5.0.0",
        "total_todos": len(todos),
        "completed": sum(1 for t in todos if t["completed"]),
        "pending": sum(1 for t in todos if not t["completed"]),
    }

# HTML 파일 서빙
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("templates/index.html", "r") as file:
        content = file.read()
    return HTMLResponse(content=content)
