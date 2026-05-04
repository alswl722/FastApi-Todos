---
name: release-test-sync
description: Use when user mentions release, version bump, "버전 업", "릴리스", or runs /release. Analyzes git diff since last tag to find new features (endpoints, model fields, UI elements) without corresponding tests, and generates test stubs in matching style. Used as part of the FastAPI Todos release pipeline.
---

# release-test-sync — 릴리스 전 누락 테스트 식별 및 stub 생성

## 목적
새 릴리스를 만들기 전에, 마지막 태그 이후 추가된 기능 중 **테스트가 누락된 영역**을 찾아 stub을 생성한다.

## 실행 단계

### Step 1: 마지막 태그 식별
```bash
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null)
```
- 실패 시(태그 없음) `HEAD~10`을 fallback으로 사용
- 결과를 사용자에게 보고: "마지막 태그: $LAST_TAG"

### Step 2: 변경 파일 분석
```bash
git diff $LAST_TAG..HEAD --name-only
git diff $LAST_TAG..HEAD -- fastapi-app/main.py
git diff $LAST_TAG..HEAD -- fastapi-app/templates/index.html
```

### Step 3: 신규 패턴 탐지

**백엔드 (main.py)**:
- 새 엔드포인트: `+@app\.(get|post|put|delete|patch)` 패턴
- 새 모델 필드: `class TodoItem` 블록의 추가된 줄
- 새 함수: `+def [a-z_]+\(`

**프론트엔드 (index.html)**:
- 새 입력 요소: 추가된 `id="..."`, `class="input-..."`
- 새 필터 버튼: `setXxxFilter`, `.xx-btn` 패턴
- 새 JS 함수: `+\s*function [a-z]+\(`

### Step 4: 기존 테스트 패턴 학습

**참고할 파일들** (반드시 먼저 읽고 스타일 파악):
- 단위 테스트 패턴: `fastapi-app/tests/test_main.py`
  - `TestCategory` 클래스 (v6.0.0에서 추가, 가장 최신 표준)
  - 7가지 테스트 케이스: 기본값/생성/필터/복합필터/수정/통계/레거시호환
- E2E 패턴: `fastapi-app/tests/e2e/`
  - `test_add_todo.py`: 폼 입력 → 검증 패턴
  - `test_filter.py`: 필터 버튼 → 결과 카드 검증
  - `conftest.py`: 공유 fixture 사용법

### Step 5: 누락 테스트 식별

각 신규 패턴에 대해:
- **백엔드 새 필드** → `test_main.py`에 `TestXxx` 클래스 누락?
- **백엔드 새 엔드포인트** → 해당 메서드 테스트 누락?
- **프론트 새 UI** → `tests/e2e/test_xxx.py` 누락?

표 형식으로 사용자에게 보고:

| 발견된 신규 기능 | 위치 | 단위 테스트 | E2E 테스트 |
|---|---|---|---|
| `category` 필드 | main.py:24 | ✅ TestCategory | ❌ 누락 |
| 카테고리 필터 UI | index.html:528 | — | ❌ 누락 |

### Step 6: 사용자 승인 받고 stub 생성

승인되면:

**단위 테스트 stub** (test_main.py에 추가):
```python
# ──────────────────────────────────────────────
# <Feature 한글 이름> 테스트 (v<VERSION> 신규)
# ──────────────────────────────────────────────
class Test<Feature>:
    def test_<feature>_default_value(self):
        """기본값 검증"""
        # TODO: 실제 어설션 채우기
        pass

    def test_<feature>_create(self):
        """생성 검증"""
        # TODO
        pass

    # ... 기존 TestCategory 패턴(7가지)을 참고해서 케이스 생성
```

**E2E 테스트 stub** (`tests/e2e/test_<feature>.py` 신규):
```python
import pytest

# Fixture는 conftest.py에 정의된 것 재사용
def test_<feature>_appears_in_form(page):
    """폼에 새 입력 요소가 보이는지"""
    # TODO: page.locator(...).is_visible() 패턴
    pass

def test_<feature>_filter_works(page):
    """필터 버튼 동작"""
    # TODO: page.click(...) → assert filtered cards
    pass
```

### Step 7: 결과 보고

생성된 파일/추가된 클래스 목록을 사용자에게 명시. **assertion은 stub 상태**로 두고, 사용자가 직접 채우거나 추가 요청하도록 안내.

## 절대 규칙

1. **assertion 자동 작성 금지** — 잘못된 어설션은 false positive를 만들어 더 위험. 항상 `# TODO` 주석으로 비워둠
2. **기존 테스트 수정 금지** — 새 케이스만 추가. 기존 테스트는 절대 건드리지 않음
3. **conftest.py 자동 수정 금지** — fixture가 필요하면 사용자에게 추가 요청만
4. **승인 없이 파일 작성 금지** — Step 5의 보고 표 보여준 뒤 사용자 "ok" 받고 진행

## 호출 컨텍스트

이 Skill은 두 경로로 호출됨:
- `/release` 슬래시 커맨드의 첫 단계 (자동)
- `version-watch.sh` Hook의 안내를 받은 Claude가 자동 호출
- 사용자가 직접 "release-test-sync 실행해줘"
