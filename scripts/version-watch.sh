#!/bin/bash
# version-watch.sh — Claude Code PostToolUse hook
#
# 역할: Edit/Write tool로 파일이 수정된 직후, 해당 파일에 버전 문자열
#       (version="X.Y.Z") 변경이 있는지 감지하여 Claude에 안내 메시지 출력.
#
# 안전성: 절대 파일을 수정하지 않음. read-only (git diff, grep, echo)만 사용.
#         무한 루프 위험 0.
#
# 입력: stdin으로 PostToolUse hook payload (JSON)
#   예: {"tool_input": {"file_path": "/path/to/file.py", ...}, ...}
#
# 출력: stdout — Claude가 다음 턴 컨텍스트로 받게 됨
#         (변경 감지 시에만 메시지, 아니면 무출력)

set -euo pipefail

# 1) stdin에서 file_path 추출
PAYLOAD=$(cat)
FILE_PATH=$(echo "$PAYLOAD" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    fp = data.get('tool_input', {}).get('file_path', '')
    print(fp)
except Exception:
    print('')
" 2>/dev/null || echo "")

# 빈 경로면 조용히 종료
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# 2) 관심 대상 파일인지 확인 (main.py / index.html / test_main.py)
case "$FILE_PATH" in
    *fastapi-app/main.py)             ;;
    *fastapi-app/templates/index.html);;
    *fastapi-app/tests/test_main.py)  ;;
    *)
        # 관심 없는 파일 → 조용히 종료
        exit 0
        ;;
esac

# 3) git 저장소 컨텍스트로 이동
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(git -C "$(dirname "$FILE_PATH")" rev-parse --show-toplevel 2>/dev/null || echo "")}"
if [ -z "$PROJECT_DIR" ] || [ ! -d "$PROJECT_DIR/.git" ]; then
    exit 0
fi

# 4) 해당 파일의 git diff에서 version="X.Y.Z" 패턴 변경이 있는지 확인
#    +/- 라인 둘 다 매치되어야 (실제 버전 변경)
DIFF_OUTPUT=$(git -C "$PROJECT_DIR" diff -- "$FILE_PATH" 2>/dev/null || echo "")

# version="X.Y.Z" 또는 "version": "X.Y.Z" 또는 v6.0.0 (HTML 뱃지) 또는 assert == "X.Y.Z"
HAS_VERSION_CHANGE=$(echo "$DIFF_OUTPUT" | grep -E '^[-+].*(version[[:space:]]*[=:][[:space:]]*"[0-9]+\.[0-9]+\.[0-9]+"|version-badge.*v[0-9]+\.[0-9]+\.[0-9]+|assert.*version.*==.*"[0-9])' | head -1 || echo "")

if [ -z "$HAS_VERSION_CHANGE" ]; then
    # 버전 변경 없음 → 조용히 종료
    exit 0
fi

# 5) 마지막 태그 정보
LAST_TAG=$(git -C "$PROJECT_DIR" describe --tags --abbrev=0 2>/dev/null || echo "(없음)")

# 6) 안내 메시지 출력 (Claude의 다음 컨텍스트로 들어감)
cat <<EOF

[version-watch hook]
⚠️  버전 문자열 변경 감지됨: $FILE_PATH
   마지막 태그: $LAST_TAG

   다음 작업이 필요할 수 있습니다:
   1) 마지막 태그 이후의 신규 기능에 대한 누락된 테스트 점검
   2) CHANGELOG 항목 추가
   3) 다른 버전 표기 파일들(main.py × 2, index.html, test_main.py)과 일관성

   진행 옵션:
   - 자동: /release 슬래시 커맨드를 사용해 전체 파이프라인 진행
   - 부분: release-test-sync skill만 호출해 누락 테스트 점검

   사용자에게 어느 쪽으로 진행할지 물어보세요.
EOF

exit 0
