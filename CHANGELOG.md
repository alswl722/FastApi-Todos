# Changelog

---

## [v6.0.0] - 2026-04-30

### 추가
- **카테고리 필드** — `TodoItem`에 `category` 필드 추가 (`work` / `study` / `exercise` / `hobby` / `other`, 기본값 `other`)
  - `GET /todos?category=work` 필터 (priority와 AND 결합 가능)
  - `GET /todos/stats` 응답에 `by_category` 카운트 추가
  - 입력 폼·편집 모달에 카테고리 select (💼 일 / 📚 공부 / 🏃 운동 / 🎨 취미 / 📌 기타)
  - 카테고리 필터 버튼 행 + 카드 좌측 inset shadow 색상 + 뱃지 표시
  - 레거시 데이터(category 필드 없음) 호환: `t.get("category", "other")`
- **Prometheus + Grafana 모니터링 스택** (`docker-compose.yml`)
  - `prom/prometheus` (포트 7070), `grafana/grafana` (포트 3000), `prom/node-exporter` (포트 7100)
  - `prometheus-fastapi-instrumentator` 적용 → `/metrics` 엔드포인트 노출
  - `prometheus-data` 볼륨 영속화, config 파일 read-only 마운트
- **테스트** — `TestCategory` 클래스 7개 추가 (모델 기본값, 생성, 필터, 복합 필터, 수정, stats, 레거시 호환)

### 변경
- `docker-compose.yml`에서 obsolete `version: "3.7"` 제거
- `requirements.txt`에 `prometheus-fastapi-instrumentator`, `prometheus-client` 추가

### 테스트 결과
```
48 passed in 0.50s  (단위 테스트, 컨테이너 내부)
```

---

## [v5.0.0] - 2026-04-12

### 추가
- **다크모드 토글** — 로컬스토리지로 사용자 선호 유지 (`localStorage.darkMode`)
- **D-day 카운트다운 뱃지** — 마감일 기반 시각화
  - `D-Day!` (오늘) / `D-3` (임박) / `D-7` (예정) / `D+1 초과` (지남)
  - 상태별 색상·애니메이션(pulse) 차등 적용
- **정렬 기능** — 기본순 / 우선순위순 / 마감일순 / 제목순 드롭다운

### 변경
- Pydantic `.dict()` → `.model_dump()` 마이그레이션 (Pydantic v2 호환)

### 품질 개선
- **SonarQube 통합** (`sonar-project.properties`)
- SonarQube 발견사항 개선: `Annotated` 타입힌트 도입, 상수 추출(`TODO_NOT_FOUND`), `responses` 문서화, float 비교 정확화
- **테스트 커버리지 100% 달성** (root 엔드포인트, `load_todos` 빈 파일 경로 추가)

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
