import os
import sys
import json
import time
import threading
import pytest
import httpx
import uvicorn

# main.py가 있는 fastapi-app/ 디렉토리를 sys.path에 추가
APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, APP_DIR)

BASE_URL = "http://127.0.0.1:8000"
TODO_FILE = os.path.join(APP_DIR, "todo.json")


# ── 서버 스레드 ─────────────────────────────────────────────────────────────────

class _UvicornThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        # main.py는 templates/와 todo.json을 상대경로로 열기 때문에
        # 서버 기동 전 작업 디렉토리를 fastapi-app/으로 변경
        os.chdir(APP_DIR)
        from main import app
        self.server = uvicorn.Server(
            uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning")
        )

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True


@pytest.fixture(scope="session")
def live_server():
    """테스트 세션 전체에서 FastAPI 서버를 한 번 기동."""
    thread = _UvicornThread()
    thread.start()
    # /health 가 200을 반환할 때까지 대기 (최대 10초)
    for _ in range(20):
        try:
            r = httpx.get(f"{BASE_URL}/health", timeout=1)
            if r.status_code == 200:
                break
        except Exception:
            pass
        time.sleep(0.5)
    else:
        raise RuntimeError("FastAPI 서버가 시간 내에 시작되지 않았습니다.")
    yield BASE_URL
    thread.stop()
    thread.join(timeout=5)


# ── 데이터 격리 ─────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clean_state(live_server):
    """매 테스트 전후 todo.json 을 빈 배열로 초기화."""
    with open(TODO_FILE, "w") as f:
        json.dump([], f)
    yield
    with open(TODO_FILE, "w") as f:
        json.dump([], f)


# ── Playwright page 픽스처 오버라이드 ──────────────────────────────────────────

@pytest.fixture
def page(page, live_server):
    """앱 홈으로 이동 후 #todo-list 가 렌더링될 때까지 대기."""
    page.goto(BASE_URL)
    page.wait_for_selector("#todo-list", state="visible")
    return page


# ── 실패 시 스크린샷 + HTML 보고서 첨부 ────────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            screenshots_dir = os.path.join(APP_DIR, "reports", "screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)
            safe_name = item.nodeid.replace("/", "_").replace("::", "_").replace(" ", "_")
            path = os.path.join(screenshots_dir, f"{safe_name}.png")
            try:
                page.screenshot(path=path, full_page=True)
                # pytest-html 보고서에 이미지 첨부
                if hasattr(report, "extras"):
                    try:
                        from pytest_html import extras as html_extras
                        report.extras.append(html_extras.image(path))
                    except Exception:
                        pass
            except Exception:
                pass


# ── Markdown 보고서 생성 ───────────────────────────────────────────────────────

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """테스트 완료 후 reports/e2e-report.md 작성."""
    reports_dir = os.path.join(APP_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    passed  = terminalreporter.stats.get("passed",  [])
    failed  = terminalreporter.stats.get("failed",  [])
    skipped = terminalreporter.stats.get("skipped", [])
    total   = len(passed) + len(failed) + len(skipped)

    lines = [
        "# E2E 테스트 보고서\n\n",
        f"**실행 일시:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n",
        f"**전체:** {total}  |  **통과:** {len(passed)}  |  "
        f"**실패:** {len(failed)}  |  **건너뜀:** {len(skipped)}\n\n",
        "## 결과 테이블\n\n",
        "| 테스트 | 결과 | 소요시간 |\n",
        "|--------|------|----------|\n",
    ]

    for r in passed:
        dur = f"{getattr(r, 'duration', 0):.2f}s"
        lines.append(f"| `{r.nodeid}` | ✅ PASS | {dur} |\n")
    for r in failed:
        dur = f"{getattr(r, 'duration', 0):.2f}s"
        lines.append(f"| `{r.nodeid}` | ❌ FAIL | {dur} |\n")
    for r in skipped:
        dur = f"{getattr(r, 'duration', 0):.2f}s"
        lines.append(f"| `{r.nodeid}` | ⏭ SKIP | {dur} |\n")

    if failed:
        lines.append("\n## 실패 상세\n\n")
        for r in failed:
            lines.append(f"### `{r.nodeid}`\n\n")
            lines.append(f"```\n{r.longreprtext}\n```\n\n")

    md_path = os.path.join(reports_dir, "e2e-report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
