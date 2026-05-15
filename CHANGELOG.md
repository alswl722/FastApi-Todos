# Changelog

---

## [v6.3.0] - 2026-05-15

### 추가
- **일기장(Diary) 기능** — 매일 일기처럼 쓸 수 있는 별도 섹션
  - `DiaryEntry` 모델: `id / date / title / content / mood` (6종 무드: happy/sad/angry/tired/love/thinking)
  - 엔드포인트: `GET /diary` (날짜 내림차순, mood 필터), `GET /diary/by-date/{date}`, `GET /diary/stats`, `POST/PUT/DELETE /diary`
  - 별도 `diary.json` 파일에 저장 (todo 데이터와 격리)
  - UI: 할 일 ↔ 일기장 탭 전환, 무드 필터 버튼, 무드별 통계 그리드, 폴라로이드 스타일 일기 카드
- **핑크 공주 테마 UI** — `templates/index.html` 전면 개편
  - Pacifico/Quicksand/Gaegu 큐트 폰트, 무지개 그라데이션 제목, 떠다니는 이모지 빤짝이 28개 (✨💖🌟🎀💕⭐🦄👑💎🌸)
  - twinkle/float-up/shimmer/wiggle/heart-beat/sparkle-spin/pulse-glow 등 9종 CSS 애니메이션
  - 핑크-골드 그라데이션 버튼, 카드, 뱃지
  - 다크모드 → 자줏빛 "밤하늘 공주모드"로 변환
- **테스트 stub** — `tests/e2e/test_diary.py` 8개 (탭 전환 / CRUD / 무드 필터, 어설션은 사람이 채움)
- **Diary 단위 테스트** — `TestDiaryModel/StateManagement/Create/Read/Update/Delete/Stats` 클래스 10개 (전부 실제 어설션 포함)

### 변경
- 제목 변경: "Minji's To-Do List" → "Princess's To-Do"

---

## [v6.2.0] - 2026-05-05

### 추가
- **메모(notes) 필드** — `TodoItem`에 `notes: Optional[str] = None` 필드 추가 (`fastapi-app/main.py`)
  - 입력 폼에 `<textarea id="notes">` 추가 (placeholder "메모 (선택)", `rows="2"`)
  - 제출 시 `notes` 값을 `POST /todos`로 전송, 빈 값은 `null`로 저장
- **테스트 stub** — `TestNotes` 클래스 7개 + `tests/e2e/test_notes.py` 5개 (assertion은 비어있음, 사용자가 채울 예정)

---

## [v6.1.0] - 2026-05-04

### 추가
- **cAdvisor 통합** — 컨테이너 메트릭 수집기 (`gcr.io/cadvisor/cadvisor`) `docker-compose.yml`에 추가
  - 포트 8080 노출, host volumes(`/`, `/var/run`, `/sys`, `/var/lib/docker/`) read-only 마운트
  - `prometheus.yml`의 scrape targets에 `cadvisor:8080` 등록 → 컨테이너별 CPU/메모리/네트워크 메트릭 수집
- **릴리스 파이프라인 자동화** (`/release` 슬래시 커맨드 + 두 Skill)
  - `release-test-sync` — 마지막 태그 이후 변경 분석, 누락 테스트 stub 식별/생성
  - `git-release-pipeline` — Conventional Commits 기반 버전 결정, 4곳 일괄 업데이트, 분리 커밋 dance, annotated tag
  - `/release [version] [--no-push]` — Phase 1~5 통합 흐름
- **버전 변경 감지 Hook** (`scripts/version-watch.sh`, `.claude/settings.json`)
  - `version="X.Y.Z"` 문자열 수정 시 `PostToolUse:Edit` hook 발동
  - Claude에 안내 메시지 주입 → `/release` 호출 제안

### 변경
- `CLAUDE.md` — 자동화 워크플로(명시 호출 + Hook), Conventional Commits 규칙, 절대 규칙 섹션 추가

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
