"""
Church Admin Dashboard v0.2 — 범용 채팅 인터페이스.

설계 원칙:
  1. 범용 채팅 — 모든 기능을 대화로 수행 (기능별 분기 없음)
  2. 기능 카드 = 대화 시작 단축키 (채팅으로 자동 전송)
  3. --resume으로 세션 연속성 — 다중 턴 대화
  4. P1 검증은 응답 후 자동 인라인 표시
  5. SOT 읽기 전용, 기존 코드 수정 없음

실행:
    cd church-admin
    streamlit run dashboard/app.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import streamlit as st

# dashboard/ 를 모듈로 import 하기 위해 경로 추가
DASHBOARD_DIR = Path(__file__).parent
PROJECT_DIR = DASHBOARD_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from dashboard.engine.claude_runner import ClaudeRunner
from dashboard.engine.sot_watcher import SOTWatcher
from dashboard.engine.command_bridge import (
    build_prompt,
    detect_card_key,
    get_card_list,
)
from dashboard.engine.context_builder import build_context
from dashboard.engine.post_execution_validator import validate_after_execution
from dashboard.components.status_panel import render_status_panel

# ─── 페이지 설정 ───
st.set_page_config(
    page_title="교회 행정 시스템",
    page_icon="⛪",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── 세션 상태 초기화 ───
if "runner" not in st.session_state:
    st.session_state.runner = ClaudeRunner(PROJECT_DIR)
if "watcher" not in st.session_state:
    st.session_state.watcher = SOTWatcher(PROJECT_DIR)
if "chat_history" not in st.session_state:
    # [{role: "user"|"assistant", content: str, validation?: ValidationResult}]
    st.session_state.chat_history = []
if "session_id" not in st.session_state:
    # Claude session ID — 후속 대화에서 --resume으로 세션 이어서
    st.session_state.session_id = None
if "last_card_key" not in st.session_state:
    st.session_state.last_card_key = None
if "summary_mtime" not in st.session_state:
    st.session_state.summary_mtime = -1.0
    st.session_state.summary_cache = {}


# ═══════════════════════════════════════════════════════════════
#  완료 처리 (렌더링 전 — invisible 처리)
#
#  Runner 완료 시 응답을 채팅에 추가하고 Runner를 리셋.
#  UI 렌더링보다 먼저 실행하여 깜빡임(flash) 방지.
# ═══════════════════════════════════════════════════════════════

_runner = st.session_state.runner
if not _runner.is_running and _runner.status in ("completed", "failed"):
    result_text = _runner.stream_state.result_text or ""

    if _runner.status == "completed":
        content = result_text.strip() or "(작업 완료)"
    else:
        content = f"오류 발생: {_runner.error}" if _runner.error else "작업 실패"

    msg: dict = {"role": "assistant", "content": content}

    # P1 독립 검증 (할루시네이션 봉쇄)
    if _runner.status == "completed":
        vr = validate_after_execution(
            card_key=st.session_state.last_card_key,
            project_dir=PROJECT_DIR,
            started_at=_runner.started_at,
        )
        if vr:
            msg["validation"] = vr

    st.session_state.chat_history.append(msg)

    # 세션 ID 보존 (후속 --resume 용)
    new_sid = _runner.stream_state.session_id
    if new_sid:
        st.session_state.session_id = new_sid

    # Runner 리셋 → idle
    st.session_state.runner = ClaudeRunner(PROJECT_DIR)
    st.session_state.summary_mtime = -1.0
    st.rerun()


runner: ClaudeRunner = st.session_state.runner
watcher: SOTWatcher = st.session_state.watcher


# ═══════════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════════

# SOT 캐시
try:
    _cur_mtime = watcher.state_path.stat().st_mtime
except OSError:
    _cur_mtime = 0.0

if _cur_mtime != st.session_state.summary_mtime:
    st.session_state.summary_cache = watcher.get_status_summary()
    st.session_state.summary_mtime = _cur_mtime

summary = st.session_state.summary_cache
church_name = summary.get("church_name", "교회 행정 시스템")

header_col1, header_col2 = st.columns([6, 1])
with header_col1:
    st.title(f"⛪ {church_name}")
with header_col2:
    if st.button("새 대화", use_container_width=True, disabled=runner.is_running):
        st.session_state.runner = ClaudeRunner(PROJECT_DIR)
        st.session_state.chat_history = []
        st.session_state.session_id = None
        st.session_state.last_card_key = None
        st.session_state.summary_mtime = -1.0
        st.rerun()

# 사이드바: 시스템 상태 요약
with st.sidebar:
    render_status_panel(summary)


# ═══════════════════════════════════════════════════════════════
#  기능 카드 (대화 비어있을 때 — 시작 화면)
# ═══════════════════════════════════════════════════════════════

if not st.session_state.chat_history and not runner.is_running:
    st.markdown("#### 무엇을 도와드릴까요?")
    st.caption("카드를 클릭하거나 아래 입력창에 자유롭게 입력하세요.")

    cards = get_card_list()
    # 2행 × 4열 레이아웃
    for row_start in range(0, len(cards), 4):
        cols = st.columns(4)
        for i, card in enumerate(cards[row_start : row_start + 4]):
            with cols[i]:
                label = f"{card['icon']} {card['label']}"
                if card.get("note"):
                    label += f"\n({card['note']})"

                if st.button(
                    label,
                    key=f"card_{card['key']}",
                    use_container_width=True,
                ):
                    # 카드 클릭 → 대화 시작
                    prompt = build_prompt(card["key"])
                    card_key = card["key"]
                    context = build_context(
                        card_key=card_key,
                        project_dir=PROJECT_DIR,
                        state=watcher.get_current_state(),
                    )
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": f"{card['icon']} {card['label']}",
                    })
                    st.session_state.last_card_key = card_key
                    try:
                        runner.start(
                            prompt=prompt,
                            system_prompt_extra=context if context else None,
                        )
                        st.rerun()
                    except RuntimeError as e:
                        st.error(str(e))

    st.divider()


# ═══════════════════════════════════════════════════════════════
#  채팅 히스토리
# ═══════════════════════════════════════════════════════════════

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # P1 검증 결과 인라인 표시 (기계적 신호)
        vr = msg.get("validation")
        if vr:
            if vr.all_passed:
                st.success(f"P1 검증 통과: {vr.summary}")
            else:
                st.error(f"P1 검증 실패: {vr.summary}")
                with st.expander("검증 상세"):
                    for check in vr.checks:
                        icon = "PASS" if check.passed else "FAIL"
                        st.markdown(f"{icon}: **{check.name}** — {check.details}")
                        if not check.passed:
                            for err in check.errors[:5]:
                                st.markdown(f"  - {err}")


# ═══════════════════════════════════════════════════════════════
#  진행 중 표시 (채팅 내 인라인)
# ═══════════════════════════════════════════════════════════════

if runner.is_running:
    with st.chat_message("assistant"):
        events = runner.stream_state.tool_events
        if events:
            latest = events[-1]
            tool_name = latest.get("tool", "작업")
            st.markdown(
                f"⏳ **처리 중...** "
                f"({tool_name} 실행 중, {len(events)}개 도구 사용)"
            )
        else:
            st.markdown("⏳ **처리 중...**")

    if st.button("🛑 취소", type="secondary"):
        runner.cancel()
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "작업이 취소되었습니다.",
        })
        st.session_state.runner = ClaudeRunner(PROJECT_DIR)
        st.rerun()

    time.sleep(2)
    st.rerun()


# ═══════════════════════════════════════════════════════════════
#  채팅 입력 (범용 — 모든 기능을 대화로)
# ═══════════════════════════════════════════════════════════════

user_input = st.chat_input(
    "메시지를 입력하세요 (예: 주보 만들어줘, 김영희 새신자 등록)",
    disabled=runner.is_running,
)

if user_input and not runner.is_running:
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
    })

    session_id = st.session_state.session_id
    runner_new = ClaudeRunner(PROJECT_DIR)
    st.session_state.runner = runner_new

    if session_id:
        # 후속 대화 — 이전 세션 이어서 (--resume)
        runner_new.start(prompt=user_input, resume_session=session_id)
    else:
        # 새 대화 — 컨텍스트 빌드 (Cold Start 해결)
        card_key = detect_card_key(user_input)
        prompt = build_prompt(user_input)
        context = build_context(
            card_key=card_key,
            project_dir=PROJECT_DIR,
            state=watcher.get_current_state(),
        )
        st.session_state.last_card_key = card_key
        runner_new.start(
            prompt=prompt,
            system_prompt_extra=context if context else None,
        )

    st.rerun()


# ═══════════════════════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════════════════════


@st.cache_data(ttl=300)
def _get_claude_version() -> str:
    """Claude Code 버전 조회 (5분 캐시)."""
    import subprocess as _sp

    try:
        result = _sp.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip().split()[-1] if result.returncode == 0 else "?"
    except Exception:
        return "?"


st.divider()
fc1, fc2 = st.columns(2)
with fc1:
    st.caption("교회 행정 시스템 Dashboard v0.2")
with fc2:
    st.caption(f"SOT: state.yaml | Claude Code CLI v{_get_claude_version()}")
