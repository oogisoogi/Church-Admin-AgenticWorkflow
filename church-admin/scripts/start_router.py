#!/usr/bin/env python3
"""
start_router.py — Smart Router with P1 Hallucination Prevention

Performs project health checks and generates execution mode options
with pre-formatted display blocks. Claude displays these blocks
VERBATIM — no interpretation, no reformatting, no hallucination.

Design principles:
  1. Read-only: Reads state.yaml only. Never writes to SOT or data files.
  2. P1 display blocks: All user-facing text is pre-computed in Python.
     Claude's role is reduced to "display and route" — not "interpret and generate."
  3. Deterministic: Same input always produces same output. No LLM judgment.
  4. Fallback-safe: If this script fails, start.md falls back to CLI mode
     (show_menu.py), preserving 100% of existing functionality.

Usage:
    python3 scripts/start_router.py --state state.yaml

Output: JSON to stdout with two sections:
  - "raw": Machine-readable data (for programmatic use)
  - "display": Pre-formatted text blocks (for Claude to display verbatim)

Exit codes:
  0 — Success (JSON output)
  1 — state.yaml not found or unparseable (JSON error output)
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    # PyYAML missing — output minimal error JSON and exit
    print(json.dumps({
        "raw": {"error": "PyYAML not installed"},
        "display": {
            "welcome_banner": "시스템 초기화 실패: PyYAML이 설치되지 않았습니다.\npip install pyyaml 을 실행해주세요.",
            "mode_question": "",
            "mode_options": [],
            "dashboard_instructions": "",
            "dashboard_unavailable": "",
        },
    }, ensure_ascii=False))
    sys.exit(1)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Minimum Streamlit version required by dashboard/app.py
# D-7 intentional duplication: dashboard/requirements.txt says streamlit>=1.30.0
# If requirements.txt changes, update this constant too.
MIN_STREAMLIT_VERSION = (1, 30)


# ---------------------------------------------------------------------------
# Health Checks (P1 deterministic)
# ---------------------------------------------------------------------------

def _check_state_yaml(state_path: str) -> tuple[dict | None, str]:
    """
    Load and validate state.yaml.

    Returns:
        (parsed_data, status_string)
        parsed_data is None if loading fails.
    """
    if not os.path.isfile(state_path):
        return None, "not_found"
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            return None, "invalid_structure"
        if "church" not in data:
            return None, "missing_church_key"
        return data, "ok"
    except yaml.YAMLError:
        return None, "yaml_parse_error"
    except OSError:
        return None, "read_error"


def _check_streamlit() -> tuple[bool, str, str]:
    """
    Check if Streamlit is installed and meets minimum version.

    Returns:
        (available, version_string, status)
    """
    try:
        import importlib
        st = importlib.import_module("streamlit")
        version_str = getattr(st, "__version__", "0.0.0")
        parts = version_str.split(".")
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        if (major, minor) >= MIN_STREAMLIT_VERSION:
            return True, version_str, "ok"
        else:
            return False, version_str, f"version_too_old (need >= {MIN_STREAMLIT_VERSION[0]}.{MIN_STREAMLIT_VERSION[1]})"
    except ImportError:
        return False, "", "not_installed"
    except (ValueError, IndexError):
        return False, "", "version_parse_error"


def _check_dashboard_app(project_dir: str) -> bool:
    """Check if dashboard/app.py exists."""
    return os.path.isfile(os.path.join(project_dir, "dashboard", "app.py"))


def _check_show_menu(project_dir: str) -> bool:
    """Check if scripts/show_menu.py exists (needed for CLI mode)."""
    return os.path.isfile(os.path.join(project_dir, "scripts", "show_menu.py"))


# ---------------------------------------------------------------------------
# Status Extraction (from state.yaml — read-only)
# ---------------------------------------------------------------------------

def _extract_quick_status(state: dict) -> dict:
    """
    Extract minimal status info from state.yaml for welcome banner.
    Does NOT read data/*.yaml files — that's show_menu.py's job.
    """
    church = state.get("church", {})

    # Validation status
    vg = church.get("verification_gates", {}).get("aggregate", {})
    total_passed = vg.get("total_passed", 0)
    total_checks = vg.get("total_checks", 0)

    # Latest bulletin
    ws_bulletin = church.get("workflow_states", {}).get("bulletin", {})
    last_issue = ws_bulletin.get("last_generated_issue", 0)
    last_date = ws_bulletin.get("last_generated_date", "")

    # System status
    system_status = church.get("status", "unknown")

    return {
        "validation_passed": total_passed,
        "validation_total": total_checks,
        "last_bulletin_issue": last_issue,
        "last_bulletin_date": last_date,
        "system_status": system_status,
    }


# ---------------------------------------------------------------------------
# P1 Display Block Generators
#
# These functions produce the EXACT text that Claude will display.
# Claude must output these strings VERBATIM — no modification allowed.
# This is the P1 hallucination prevention layer.
# ---------------------------------------------------------------------------

def _generate_welcome_banner(church_name: str, status: dict) -> str:
    """Generate the welcome banner text block."""
    vp = status["validation_passed"]
    vt = status["validation_total"]
    validation_text = f"{vp}/{vt} 통과" if vt > 0 else "미확인"

    issue = status["last_bulletin_issue"]
    bdate = status["last_bulletin_date"]
    bulletin_text = f"#{issue} ({bdate})" if issue else "없음"

    sys_status = status["system_status"]
    sys_text = "정상 가동 중" if sys_status == "active" else sys_status

    return (
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"  ⛪ {church_name}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"\n"
        f"시스템 상태:\n"
        f"  데이터 무결성: {validation_text}\n"
        f"  최근 주보: {bulletin_text}\n"
        f"  시스템: {sys_text}"
    )


def _generate_mode_options(cli_available: bool, dashboard_available: bool) -> list[dict]:
    """Generate AskUserQuestion options — Claude uses these EXACTLY."""
    options = []

    if cli_available:
        options.append({
            "label": "대화형 모드 (CLI)",
            "description": "터미널에서 메뉴를 선택하고, 한 단계씩 대화하며 작업합니다",
        })

    if dashboard_available:
        options.append({
            "label": "대시보드 모드 (Web UI)",
            "description": "웹 브라우저에서 시각적으로 작업합니다",
        })
    else:
        options.append({
            "label": "대시보드 모드 (Web UI) — 설치 필요",
            "description": "Streamlit 설치 후 사용 가능합니다",
        })

    return options


def _generate_dashboard_instructions(project_dir: str) -> str:
    """Generate dashboard launch instructions with absolute path."""
    abs_path = os.path.abspath(project_dir)
    return (
        f"다음 명령어를 새 터미널에서 실행하세요:\n"
        f"\n"
        f"  cd {abs_path}\n"
        f"  streamlit run dashboard/app.py\n"
        f"\n"
        f"브라우저에서 http://localhost:8501 이 자동으로 열립니다.\n"
        f"\n"
        f"⚠ 대시보드 사용 중에는 이 CLI 세션에서 데이터 수정 작업을 하지 마세요.\n"
        f"  두 곳에서 동시에 작업하면 데이터 불일치가 발생할 수 있습니다."
    )


def _generate_dashboard_unavailable(streamlit_status: str) -> str:
    """Generate message when dashboard is not available."""
    if streamlit_status == "not_installed":
        return (
            "대시보드를 사용하려면 먼저 Streamlit 설치가 필요합니다:\n"
            "\n"
            "  pip install 'streamlit>=1.30.0'\n"
            "\n"
            "설치 후 다시 '시작'을 입력해주세요."
        )
    elif "version_too_old" in streamlit_status:
        return (
            "설치된 Streamlit 버전이 너무 낮습니다. 업그레이드가 필요합니다:\n"
            "\n"
            "  pip install --upgrade 'streamlit>=1.30.0'\n"
            "\n"
            "업그레이드 후 다시 '시작'을 입력해주세요."
        )
    else:
        return (
            "대시보드를 사용할 수 없습니다.\n"
            "dashboard/app.py 파일이 존재하는지 확인해주세요."
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate_start_route(state_path: str, project_dir: str) -> dict:
    """
    Generate the complete start routing response.

    Returns dict with:
      - raw: machine-readable data
      - display: pre-formatted text blocks for Claude to display verbatim
    """
    # --- Health checks ---
    state_data, state_status = _check_state_yaml(state_path)
    streamlit_available, streamlit_version, streamlit_status = _check_streamlit()
    dashboard_app_exists = _check_dashboard_app(project_dir)
    show_menu_exists = _check_show_menu(project_dir)

    # --- Mode availability ---
    cli_available = (state_status == "ok") and show_menu_exists
    dashboard_available = streamlit_available and dashboard_app_exists

    # --- Extract status (if state.yaml is valid) ---
    if state_data:
        church = state_data.get("church", {})
        church_name = church.get("name", "교회")
        quick_status = _extract_quick_status(state_data)
    else:
        church_name = "교회"
        quick_status = {
            "validation_passed": 0,
            "validation_total": 0,
            "last_bulletin_issue": 0,
            "last_bulletin_date": "",
            "system_status": "unknown",
        }

    # --- Build P1 display blocks ---
    welcome_banner = _generate_welcome_banner(church_name, quick_status)
    mode_question = "실행 모드를 선택해주세요."
    mode_options = _generate_mode_options(cli_available, dashboard_available)

    if dashboard_available:
        dashboard_instructions = _generate_dashboard_instructions(project_dir)
        dashboard_unavailable = ""
    else:
        dashboard_instructions = ""
        dashboard_unavailable = _generate_dashboard_unavailable(streamlit_status)

    # --- Assemble response ---
    return {
        "raw": {
            "church_name": church_name,
            "init_checks": {
                "state_yaml": state_status,
                "streamlit": streamlit_status,
                "streamlit_version": streamlit_version,
                "dashboard_app": "ok" if dashboard_app_exists else "not_found",
                "show_menu": "ok" if show_menu_exists else "not_found",
            },
            "modes": [
                {
                    "key": "cli",
                    "available": cli_available,
                },
                {
                    "key": "dashboard",
                    "available": dashboard_available,
                },
            ],
        },
        "display": {
            "welcome_banner": welcome_banner,
            "mode_question": mode_question,
            "mode_options": mode_options,
            "dashboard_instructions": dashboard_instructions,
            "dashboard_unavailable": dashboard_unavailable,
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Church Admin Smart Router — P1 Hallucination Prevention"
    )
    parser.add_argument(
        "--state",
        default="state.yaml",
        help="Path to state.yaml (default: state.yaml)",
    )
    parser.add_argument(
        "--project-dir",
        default=".",
        help="Path to church-admin project directory (default: current directory)",
    )
    args = parser.parse_args()

    result = generate_start_route(args.state, args.project_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # Exit code: 0 if state.yaml is valid, 1 otherwise
    if result["raw"]["init_checks"]["state_yaml"] != "ok":
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        # Fallback — script failure should never block the start flow
        print(json.dumps({
            "raw": {"error": str(e)},
            "display": {
                "welcome_banner": "시스템 초기화 중 오류가 발생했습니다.",
                "mode_question": "",
                "mode_options": [],
                "dashboard_instructions": "",
                "dashboard_unavailable": "",
            },
        }, ensure_ascii=False))
        sys.exit(1)
