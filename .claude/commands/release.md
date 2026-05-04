---
description: 릴리스 파이프라인 자동화 — 누락 테스트 생성 + 버전 결정 + CHANGELOG + 분리 커밋 + 태그 + 푸시
---

# /release — FastAPI Todos 릴리스 파이프라인

## 인자 처리

사용자가 `/release` 뒤에 인자를 줄 수 있다:
- `/release` → 자동으로 다음 버전 결정 (Conventional Commits 분석)
- `/release v7.0.0` → 명시적 버전 지정
- `/release --no-push` → 푸시 직전까지만 진행, 푸시는 사용자가 직접

인자: $ARGUMENTS

## 실행 흐름

### Phase 1 — 사전 점검

1. 현재 working tree 상태 확인:
   ```bash
   git status --short
   ```
   uncommitted 변경이 있으면 사용자에게 "먼저 커밋하거나 stash 후 진행하세요" 안내 후 중단. (단, 의도적으로 release 작업 중 변경분이 있을 수 있으므로 무엇이 unstaged인지 보고)

2. 마지막 태그와 그 이후 커밋 수 확인:
   ```bash
   git describe --tags --abbrev=0
   git log --oneline $(git describe --tags --abbrev=0)..HEAD | wc -l
   ```
   커밋이 0개면 "릴리스할 변경사항이 없습니다" 안내 후 중단.

### Phase 2 — release-test-sync Skill 호출

`release-test-sync` Skill을 호출하여:
- 마지막 태그 이후의 변경 분석
- 누락된 테스트 stub 식별
- 사용자 승인 후 stub 생성

이 단계에서 Skill이 사용자 승인을 받아 테스트 파일을 생성하면 working tree에 변경분이 생긴다. (일단 commit 안 함)

### Phase 3 — git-release-pipeline Skill 호출

`git-release-pipeline` Skill을 호출하여:
- 다음 버전 자동 결정 (또는 인자로 받은 버전 사용)
- 버전 strings 4곳 일괄 업데이트
- CHANGELOG 항목 작성
- 분리 커밋 자동 dance (test → version → CHANGELOG)
- Annotated tag 생성

### Phase 4 — 푸시 (조건부)

- `--no-push` 인자가 있으면: 여기서 종료. "푸시는 직접 진행하세요. 명령어: `git push origin main && git push origin <tag>`" 안내.
- 그 외: 사용자에게 명시 승인 받고 푸시 실행.

### Phase 5 — 결과 보고

릴리스 후 사용자에게 다음을 보고:

```
✅ v<VERSION> 릴리스 완료

생성된 커밋:
  <hash> test: v<VERSION> 누락 테스트 추가
  <hash> chore: v<VERSION> 버전 업
  <hash> docs: CHANGELOG v<VERSION> 정리

생성된 태그:
  v<VERSION> (annotated)

GitHub Release 노트 초안:
<제목>
<본문 마크다운>

GitHub에서 https://github.com/alswl722/FastApi-Todos/releases/new?tag=v<VERSION> 으로 릴리스 페이지 작성 가능합니다.
```

## 안전 규칙

1. **사용자 승인 없이 push 금지**
2. **인자로 받은 버전이 기존 태그와 같으면 중단** — 중복 태그 방지
3. **인자로 받은 버전이 마지막 태그보다 작으면 중단** — semver 역행 방지
4. **테스트 stub의 assertion은 빈 채로 둠** — 자동 작성 금지

## 사용 예시

### 일반 흐름
```
사용자: /release
Claude: [분석] 마지막 태그 v6.0.0, 이후 2개 커밋 (feat 1, chore 1)
        → 권장: v6.1.0
사용자: ok
Claude: [release-test-sync 실행] 누락 테스트 3개 식별 → stub 생성
사용자: 좋아요
Claude: [git-release-pipeline 실행] 분리 커밋 3개 + 태그 생성
        푸시할까요?
사용자: 네
Claude: [푸시] 완료
```

### 명시 버전 + push 보류
```
사용자: /release v7.0.0 --no-push
Claude: ... (Phase 1~3까지만, Phase 4 건너뛰고 종료)
```
