# FastAPI Todos — 프로젝트 가이드

FastAPI 기반 To-Do 리스트 서비스. v6.0.0까지 배포된 상태. CRUD + 검색 + 필터(priority, category) + 통계 + 다크모드 + D-day + 정렬 + Prometheus/Grafana 모니터링.

## 자동화 워크플로

이 프로젝트는 두 가지 릴리스 자동화 경로가 설정되어 있다:

### 명시 호출 — `/release [version] [--no-push]`
- 인자 없으면: Conventional Commits 분석으로 다음 버전 자동 결정
- 인자 있으면: 명시적 버전 지정
- 흐름: 누락 테스트 stub 생성 → 버전 4곳 업데이트 → CHANGELOG → 분리 커밋 → 태그 → 푸시(승인 필수)

### 자동 감지 — Hook
- `version="X.Y.Z"` 문자열을 수정하면 `scripts/version-watch.sh` Hook이 발동
- Claude에 안내 메시지가 주입됨 → `/release` 또는 `release-test-sync` 호출 제안

## Conventional Commits 규칙 (필수)

모든 커밋 메시지는 다음 prefix로 시작:
- `feat:` 새 기능 (MINOR bump)
- `fix:` 버그 수정 (PATCH bump)
- `chore:` 잡일 (의존성, 설정)
- `docs:` 문서
- `refactor:` 리팩토링
- `test:` 테스트
- `perf:` 성능 개선
- Breaking change: `feat!:` 또는 본문에 `BREAKING CHANGE:` (MAJOR bump)

## 절대 규칙

1. **main 직접 push 금지** — `/release` 경유 또는 PR로
2. **분리 커밋 우선** — 단일 변경분이 여러 의미 단위면 분리
3. **assertion 자동 작성 금지** — 테스트 stub의 어설션은 사람이 채움
4. **자동 push 금지** — 푸시는 항상 사용자 명시 승인 후

## 테스트

단위 + E2E 모두 컨테이너에서 실행:
```bash
docker compose build fastapi-app
docker run --rm fastapi_todos-fastapi-app:latest python -m pytest tests/test_main.py
```

## 핵심 파일

- 백엔드: `fastapi-app/main.py`
- 프론트: `fastapi-app/templates/index.html`
- 단위 테스트: `fastapi-app/tests/test_main.py`
- E2E 테스트: `fastapi-app/tests/e2e/`
- 모니터링: `prometheus/prometheus.yml`, `docker-compose.yml`
