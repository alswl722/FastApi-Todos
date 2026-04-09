# Changelog

---

## [v4.1.0] - 2026-04-09

### 추가
- **Playwright E2E 테스트** 39개 추가 (`tests/e2e/`)
  - `test_page_load.py` — 페이지 로드 및 UI 요소 존재 확인 (6개)
  - `test_add_todo.py` — 할 일 추가 폼 동작 (6개)
  - `test_toggle_todo.py` — 완료 토글 및 통계 연동 (3개)
  - `test_filter.py` — 상태/우선순위 필터 (5개)
  - `test_search.py` — 키워드 검색 및 초기화 (4개)
  - `test_delete_todo.py` — 삭제 확인/취소/빈 상태 (4개)
  - `test_edit_todo.py` — 수정 모달 동작 (6개)
  - `test_statistics.py` — 통계 대시보드 수치 갱신 (5개)
- **자동 보고서 생성**
  - `reports/e2e-report.html` — pytest-html 자기완결형 보고서
  - `reports/e2e-report.md` — Markdown 결과 테이블 + 실패 상세
  - `reports/screenshots/` — 실패 시 전체 페이지 스크린샷 자동 저장
- **`pytest.ini`** — `e2e` / `unit` 마커 설정, 분리 실행 지원
- **`requirements.txt`** — `playwright`, `pytest-playwright` 추가

### 테스트 결과
```
39 passed in 10.32s  (Chromium headless)
```

### 실행 방법
```bash
# E2E 테스트 + 보고서 생성
python3 -m pytest -m e2e tests/e2e/ \
  --html=reports/e2e-report.html \
  --self-contained-html \
  --browser chromium -v

# 기존 단위 테스트만
python3 -m pytest -m "not e2e" -v

# 디버깅 (브라우저 창 표시)
python3 -m pytest -m e2e --headed --slowmo=500 tests/e2e/
```

---

## [v4.0.0] - 2026-04-09

### 추가
- 통계 대시보드 (전체/완료/미완료 수치, 완료율 프로그레스바)
- 우선순위(priority) 필터 버튼 (전체/높음/보통/낮음)
- 우선순위별 막대 그래프

---

## [v3.0.0]

- 우선순위(priority) 필드 추가 (low / medium / high)
- 마감일(due_date) 필드 추가
- 초과 마감일 경고 표시

---

## [v2.0.0]

- 검색 기능 추가 (`/todos/search`)
- 상태 필터 (전체/미완료/완료)
- 할 일 수정 모달

---

## [v1.0.0]

- FastAPI 기반 Todo CRUD API
- JSON 파일 영속성 저장
- Vanilla JS SPA 프론트엔드
