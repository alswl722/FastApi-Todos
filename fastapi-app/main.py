from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Annotated, Optional
import json
import os
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="Minji's Todo List",
    description="VDI 배포 과제용 업그레이드 버전",
    version="6.3.0"
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# To-Do 항목 모델
class TodoItem(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    priority: str = "medium"       # low / medium / high
    category: str = "other"        # work / study / exercise / hobby / other
    due_date: Optional[str] = None # YYYY-MM-DD
    notes: Optional[str] = None    # 메모 (자유 텍스트)

# 일기 항목 모델
class DiaryEntry(BaseModel):
    id: int
    date: str                      # YYYY-MM-DD
    title: str
    content: str
    mood: str = "happy"            # happy / sad / angry / tired / love / thinking

# JSON 파일 경로
TODO_FILE = "todo.json"
DIARY_FILE = "diary.json"

# 템플릿 절대경로 — cwd 무관하게 동작 (Docker/Jenkins/로컬 어디서든)
TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "index.html")

TODO_NOT_FOUND = "To-Do item not found"
DIARY_NOT_FOUND = "Diary entry not found"

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

# JSON 파일에서 일기 항목 로드
def load_diary():
    if os.path.exists(DIARY_FILE):
        with open(DIARY_FILE, "r") as file:
            return json.load(file)
    return []

# JSON 파일에 일기 항목 저장
def save_diary(entries):
    with open(DIARY_FILE, "w") as file:
        json.dump(entries, file, indent=4, ensure_ascii=False)

# To-Do 목록 조회 (priority / completed 필터 지원)
@app.get("/todos", response_model=list[TodoItem])
def get_todos(
    priority: Annotated[Optional[str], Query(description="low / medium / high")] = None,
    category: Annotated[Optional[str], Query(description="work / study / exercise / hobby / other")] = None,
    completed: Annotated[Optional[bool], Query(description="true / false")] = None,
):
    todos = load_todos()
    if priority is not None:
        todos = [t for t in todos if t["priority"] == priority]
    if category is not None:
        todos = [t for t in todos if t.get("category", "other") == category]
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
        "by_category": {
            "work":     sum(1 for t in todos if t.get("category", "other") == "work"),
            "study":    sum(1 for t in todos if t.get("category", "other") == "study"),
            "exercise": sum(1 for t in todos if t.get("category", "other") == "exercise"),
            "hobby":    sum(1 for t in todos if t.get("category", "other") == "hobby"),
            "other":    sum(1 for t in todos if t.get("category", "other") == "other"),
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
@app.put("/todos/{todo_id}", response_model=TodoItem, responses={404: {"description": TODO_NOT_FOUND}})
def update_todo(todo_id: int, updated_todo: TodoItem):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo.update(updated_todo.model_dump())
            save_todos(todos)
            return updated_todo
    raise HTTPException(status_code=404, detail=TODO_NOT_FOUND)

# 완료 상태만 토글
@app.patch("/todos/{todo_id}/toggle", responses={404: {"description": TODO_NOT_FOUND}})
def toggle_todo(todo_id: int):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo["completed"] = not todo["completed"]
            save_todos(todos)
            return todo
    raise HTTPException(status_code=404, detail=TODO_NOT_FOUND)

# To-Do 항목 삭제
@app.delete("/todos/{todo_id}", responses={404: {"description": TODO_NOT_FOUND}})
def delete_todo(todo_id: int):
    todos = load_todos()
    new_todos = [todo for todo in todos if todo["id"] != todo_id]
    if len(new_todos) == len(todos):
        raise HTTPException(status_code=404, detail=TODO_NOT_FOUND)
    save_todos(new_todos)
    return {"message": "To-Do item deleted"}

# 서버 상태 확인
@app.get("/health")
def health_check():
    todos = load_todos()
    return {
        "status": "ok",
        "version": "6.3.0",
        "total_todos": len(todos),
        "completed": sum(1 for t in todos if t["completed"]),
        "pending": sum(1 for t in todos if not t["completed"]),
    }

# ──────────────────────────────────────────────
# 일기장 (Diary) API
# ──────────────────────────────────────────────

# 일기 목록 조회 (mood 필터 + 날짜 정렬)
@app.get("/diary", response_model=list[DiaryEntry])
def get_diary_entries(
    mood: Annotated[Optional[str], Query(description="happy / sad / angry / tired / love / thinking")] = None,
):
    entries = load_diary()
    if mood is not None:
        entries = [e for e in entries if e.get("mood", "happy") == mood]
    entries.sort(key=lambda e: e.get("date", ""), reverse=True)
    return entries

# 특정 날짜의 일기 조회
@app.get("/diary/by-date/{date}", response_model=list[DiaryEntry])
def get_diary_by_date(date: str):
    entries = load_diary()
    return [e for e in entries if e.get("date") == date]

# 일기 통계
@app.get("/diary/stats")
def get_diary_stats():
    entries = load_diary()
    total = len(entries)
    return {
        "total": total,
        "by_mood": {
            "happy":    sum(1 for e in entries if e.get("mood", "happy") == "happy"),
            "sad":      sum(1 for e in entries if e.get("mood", "happy") == "sad"),
            "angry":    sum(1 for e in entries if e.get("mood", "happy") == "angry"),
            "tired":    sum(1 for e in entries if e.get("mood", "happy") == "tired"),
            "love":     sum(1 for e in entries if e.get("mood", "happy") == "love"),
            "thinking": sum(1 for e in entries if e.get("mood", "happy") == "thinking"),
        },
    }

# 신규 일기 추가
@app.post("/diary", response_model=DiaryEntry)
def create_diary_entry(entry: DiaryEntry):
    entries = load_diary()
    entries.append(entry.model_dump())
    save_diary(entries)
    return entry

# 일기 수정
@app.put("/diary/{entry_id}", response_model=DiaryEntry, responses={404: {"description": DIARY_NOT_FOUND}})
def update_diary_entry(entry_id: int, updated: DiaryEntry):
    entries = load_diary()
    for entry in entries:
        if entry["id"] == entry_id:
            entry.update(updated.model_dump())
            save_diary(entries)
            return updated
    raise HTTPException(status_code=404, detail=DIARY_NOT_FOUND)

# 일기 삭제
@app.delete("/diary/{entry_id}", responses={404: {"description": DIARY_NOT_FOUND}})
def delete_diary_entry(entry_id: int):
    entries = load_diary()
    new_entries = [e for e in entries if e["id"] != entry_id]
    if len(new_entries) == len(entries):
        raise HTTPException(status_code=404, detail=DIARY_NOT_FOUND)
    save_diary(new_entries)
    return {"message": "Diary entry deleted"}

# HTML 파일 서빙
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open(TEMPLATE_PATH, "r") as file:
        content = file.read()
    return HTMLResponse(content=content)
