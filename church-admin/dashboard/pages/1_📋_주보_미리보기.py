"""
주보 미리보기 — 2단 레이아웃 주보 뷰어.

bulletin-data.yaml 데이터를 신문 스타일 2단 레이아웃으로 렌더링.
대시보드 사이드바에서 "주보 미리보기"로 접근 가능.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# 프로젝트 경로 설정
DASHBOARD_DIR = Path(__file__).parent.parent
PROJECT_DIR = DASHBOARD_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from dashboard.components.bulletin_viewer import render_bulletin

st.set_page_config(
    page_title="주보 미리보기",
    page_icon="📋",
    layout="wide",
)

# ── Header ──
st.title("📋 주보 미리보기")
st.caption("bulletin-data.yaml 기반 2단 레이아웃 미리보기 — 인쇄용 주보 형태")

st.divider()

# ── Bulletin Render ──
render_bulletin(PROJECT_DIR)

# ── Footer ──
st.divider()
col1, col2 = st.columns(2)
with col1:
    bulletin_path = PROJECT_DIR / "data" / "bulletin-data.yaml"
    if bulletin_path.exists():
        import yaml
        with open(bulletin_path, encoding="utf-8") as f:
            bdata = yaml.safe_load(f)
        b = bdata.get("bulletin", {})
        st.caption(f"제 {b.get('issue_number', '?')}호 | {b.get('date', '?')}")
with col2:
    st.caption("교회 행정 시스템 Dashboard v0.2")
