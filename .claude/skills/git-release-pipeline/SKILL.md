---
name: git-release-pipeline
description: Use when user is ready to release a new version after tests are in place. Performs the full release pipeline - determines next version from Conventional Commits, updates version strings in 4 locations, generates CHANGELOG entry, creates separated commits in the established v6.0.0 dance pattern, creates annotated tag, and pushes (with explicit user approval). For FastAPI Todos project.
---

# git-release-pipeline — 릴리스 파이프라인 자동화

## 목적
릴리스에 필요한 git 작업 일체를 자동화: 버전 결정 → 버전 strings 일괄 업데이트 → CHANGELOG 작성 → 분리 커밋 → 태그 → 푸시.

**전제**: `release-test-sync`가 먼저 실행되어 테스트가 정리된 상태여야 한다.

## 실행 단계

### Step 1: Conventional Commits 분석으로 다음 버전 결정

```bash
LAST_TAG=$(git describe --tags --abbrev=0)
git log $LAST_TAG..HEAD --format=%s
```

분류 규칙:
| 패턴 | 종류 | 예시 |
|---|---|---|
| `BREAKING CHANGE:` 본문 또는 `feat!:`/`fix!:` | **MAJOR** | v6.0.0 → v7.0.0 |
| `feat:` 포함 | **MINOR** | v6.0.0 → v6.1.0 |
| `fix:` / `refactor:` / `perf:` 만 | **PATCH** | v6.0.0 → v6.0.1 |
| `chore:` / `docs:` / `test:` 만 | (릴리스 불필요) | 사용자 확인 |

**사용자에게 권장 버전 보고**:
```
마지막 태그: v6.0.0
이후 커밋:
  - feat: 카테고리 필드 추가 (8846ed4)
  - chore: cAdvisor 추가 (f8f3c24)
→ 권장 다음 버전: v6.1.0 (MINOR — feat 1건 발견, BREAKING 없음)
이대로 진행할까요? (또는 다른 버전 명시)
```

사용자가 인자로 명시 (`/release v7.0.0`)했다면 자동 결정 무시.

### Step 2: 버전 문자열 4곳 일괄 업데이트

업데이트 대상:
1. `fastapi-app/main.py` line ~12: `version="X.Y.Z"`
2. `fastapi-app/main.py` line ~138: `"version": "X.Y.Z",`
3. `fastapi-app/templates/index.html` line ~461: `<span class="version-badge">vX.Y.Z</span>`
4. `fastapi-app/tests/test_main.py` line ~399: `assert data["version"] == "X.Y.Z"`

⚠️ **주의**: 라인 번호는 시간이 지나면 변경될 수 있음. 먼저 grep으로 정확한 위치 확인:
```bash
grep -rn "X\.Y\.Z" fastapi-app/ --include="*.py" --include="*.html"
```
(여기서 `X.Y.Z`는 현재 버전, 예: `6\.0\.0`)

### Step 3: CHANGELOG 항목 자동 작성

[CHANGELOG.md](CHANGELOG.md)의 v5.0.0/v6.0.0 형식 참고:

```markdown
## [v<NEW_VERSION>] - YYYY-MM-DD

### 추가
- (feat: 커밋들에서 추출한 항목)

### 변경
- (refactor: / perf: 커밋들)

### 수정
- (fix: 커밋들)

### 품질 개선
- (test: / chore: 중 의미있는 것)
```

git log 메시지 첫 줄에서 prefix 제거하고 본문만 추출:
```bash
git log $LAST_TAG..HEAD --format="- %s" | sed -E 's/^- (feat|fix|chore|docs|refactor|test|perf):\s*/- /'
```

새 항목을 [CHANGELOG.md](CHANGELOG.md) 첫 `---` 위에 삽입 (v6.0.0 항목 위로).

### Step 4: 분리 커밋 자동 dance (v6.0.0 검증된 패턴)

**현재 working tree 상태 가정**: `release-test-sync`가 추가한 새 테스트 파일 + Step 2에서 수정한 버전 strings + Step 3에서 수정한 CHANGELOG가 모두 unstaged.

**커밋 분리 절차**:

#### Commit 1: 테스트 추가 (있는 경우)
```bash
# 신규/수정된 테스트 파일만
git add fastapi-app/tests/
git commit -m "test: v<NEW_VERSION> 누락 테스트 추가

<release-test-sync가 식별한 신규 기능별 테스트 stub>

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

#### Commit 2: 버전 bump
```bash
# 버전 strings 임시 되돌리기 (Step 2에서 한 변경 reset만)
# 또는 stash 활용
# 핵심: 기능 변경분이 있다면 commit 2 전에 분리 필요

# 버전 strings 재적용
git add fastapi-app/main.py fastapi-app/templates/index.html fastapi-app/tests/test_main.py
git commit -m "chore: v<NEW_VERSION> 버전 업

- FastAPI 앱 메타, /health 응답, 헤더 뱃지, 테스트 단언 일괄 갱신

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

#### Commit 3: CHANGELOG
```bash
git add CHANGELOG.md
git commit -m "docs: CHANGELOG v<NEW_VERSION> 정리

<주요 항목 1-2줄 요약>

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Step 5: Annotated tag 생성

CHANGELOG의 새 항목에서 본문 추출해 태그 메시지로 사용:

```bash
git tag -a v<NEW_VERSION> -m "v<NEW_VERSION> - <한 줄 요약>

<CHANGELOG의 추가/변경 섹션 내용>"
```

### Step 6: 푸시 (사용자 명시 승인 필수)

⚠️ **자동 실행 금지**. 반드시 사용자에게:

```
다음 작업을 진행할까요?
  - git push origin main  (3 commits)
  - git push origin v<NEW_VERSION>  (1 tag)

[y/n] 또는 --no-push로 시작했으면 여기까지로 종료.
```

승인 받은 경우만:
```bash
git push origin main
git push origin v<NEW_VERSION>
```

## 절대 규칙

1. **승인 없는 push 금지** — Step 6은 반드시 명시 승인
2. **분리 커밋 dance 시 stash 우선** — `git stash` / `git stash pop`으로 안전하게 (직접 파일 revert는 실수 위험)
3. **기존 커밋 amend 금지** — 항상 새 커밋으로
4. **버전 number 라인 직접 가정 금지** — grep으로 현재 위치 확인
5. **CHANGELOG 사용자 직접 편집 가능성 체크** — `git diff CHANGELOG.md` 먼저 보고 conflict 확인

## 호출 컨텍스트

- `/release` 슬래시 커맨드의 두번째 단계 (release-test-sync 이후)
- 사용자가 직접 "git-release-pipeline 실행해줘"
- 분리 호출도 가능: `/release` 없이 그냥 "이거 v7.0.0으로 릴리스해줘" 같은 자연어로도 트리거

## 실패 시 복구

분리 커밋 도중 실패하면:
```bash
git reset --soft HEAD~N    # N = 만든 커밋 수, working tree 보존
# 또는
git reset --hard <last-known-good>  # 신중하게
```
사용자에게 현재 상태 보고하고 다음 단계 결정 요청.
