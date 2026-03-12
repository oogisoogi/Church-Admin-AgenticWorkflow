"""
Bulletin Viewer — 2단 주보 미리보기 컴포넌트.

bulletin-data.yaml을 읽어 신문 스타일 2단 레이아웃으로 렌더링.
인쇄 가능한 A4 비율의 미리보기를 Streamlit 내에서 제공.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st
import yaml


def _load_bulletin_data(project_dir: Path) -> dict | None:
    """bulletin-data.yaml을 로드."""
    path = project_dir / "data" / "bulletin-data.yaml"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _get_bulletin_css() -> str:
    """2단 주보 레이아웃 CSS."""
    return """
<style>
.bulletin-container {
    max-width: 900px;
    margin: 0 auto;
    font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
    background: #ffffff;
    border: 1px solid #d0d0d0;
    box-shadow: 0 2px 12px rgba(0,0,0,0.1);
    border-radius: 4px;
    overflow: hidden;
}

/* ── Header ── */
.bulletin-header {
    background: linear-gradient(135deg, #1a3a5c 0%, #2d5a87 100%);
    color: white;
    text-align: center;
    padding: 28px 20px 22px;
    position: relative;
}
.bulletin-header::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 60px;
    height: 3px;
    background: #c9a84c;
}
.bulletin-church-name {
    font-size: 26px;
    font-weight: 700;
    letter-spacing: 4px;
    margin-bottom: 6px;
}
.bulletin-subtitle {
    font-size: 12px;
    opacity: 0.85;
    letter-spacing: 2px;
}
.bulletin-date-bar {
    display: flex;
    justify-content: center;
    gap: 24px;
    margin-top: 12px;
    font-size: 13px;
    opacity: 0.9;
}

/* ── Sermon Banner ── */
.sermon-banner {
    background: #f7f4ee;
    border-bottom: 1px solid #e0dcd4;
    padding: 18px 24px;
    text-align: center;
}
.sermon-series {
    font-size: 11px;
    color: #8a7a5a;
    letter-spacing: 1px;
    margin-bottom: 4px;
}
.sermon-title {
    font-size: 22px;
    font-weight: 700;
    color: #2c1810;
    margin-bottom: 6px;
}
.sermon-scripture {
    font-size: 13px;
    color: #5a4a3a;
}
.sermon-preacher {
    font-size: 12px;
    color: #8a7a6a;
    margin-top: 4px;
}

/* ── Two Columns ── */
.bulletin-body {
    display: flex;
    gap: 0;
    min-height: 500px;
}
.bulletin-col-left {
    flex: 1;
    padding: 20px;
    border-right: 1px solid #e8e4dc;
}
.bulletin-col-right {
    flex: 1;
    padding: 20px;
}

/* ── Section headers ── */
.section-header {
    font-size: 14px;
    font-weight: 700;
    color: #1a3a5c;
    border-bottom: 2px solid #1a3a5c;
    padding-bottom: 4px;
    margin-bottom: 12px;
    margin-top: 18px;
    letter-spacing: 1px;
}
.section-header:first-child {
    margin-top: 0;
}

/* ── Worship Order Table ── */
.worship-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    line-height: 1.6;
}
.worship-table th {
    background: #f0ede6;
    color: #4a4a4a;
    font-weight: 600;
    font-size: 11px;
    padding: 5px 6px;
    text-align: left;
    border-bottom: 1px solid #d8d4cc;
}
.worship-table td {
    padding: 5px 6px;
    border-bottom: 1px solid #eceae4;
    vertical-align: top;
}
.worship-table tr:last-child td {
    border-bottom: none;
}
.worship-num {
    text-align: center;
    color: #1a3a5c;
    font-weight: 700;
    width: 28px;
}

/* ── Announcements ── */
.announcement-item {
    margin-bottom: 10px;
    font-size: 12px;
    line-height: 1.65;
}
.announcement-title {
    font-weight: 700;
    color: #2c1810;
}
.announcement-badge {
    display: inline-block;
    background: #c0392b;
    color: white;
    font-size: 9px;
    font-weight: 700;
    padding: 1px 5px;
    border-radius: 2px;
    margin-right: 4px;
    vertical-align: middle;
}

/* ── Prayer Requests ── */
.prayer-item {
    margin-bottom: 8px;
    font-size: 12px;
    line-height: 1.6;
    padding-left: 12px;
    position: relative;
}
.prayer-item::before {
    content: '✦';
    position: absolute;
    left: 0;
    color: #c9a84c;
    font-size: 8px;
    top: 3px;
}
.prayer-category {
    font-weight: 600;
    color: #1a3a5c;
}

/* ── Celebrations ── */
.celebration-item {
    font-size: 12px;
    line-height: 1.8;
    padding-left: 12px;
    position: relative;
}
.celebration-item::before {
    content: '🎂';
    position: absolute;
    left: -2px;
    font-size: 10px;
}

/* ── Offering Team ── */
.offering-team {
    font-size: 12px;
    color: #5a5a5a;
    line-height: 1.6;
    text-align: center;
    padding: 8px;
    background: #faf8f4;
    border-radius: 3px;
}

/* ── Footer / Next Week ── */
.bulletin-footer {
    background: #f7f4ee;
    border-top: 1px solid #e0dcd4;
    padding: 16px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.next-week-box {
    flex: 1;
}
.next-week-label {
    font-size: 11px;
    color: #8a7a5a;
    letter-spacing: 1px;
    margin-bottom: 4px;
}
.next-week-title {
    font-size: 15px;
    font-weight: 700;
    color: #2c1810;
}
.next-week-scripture {
    font-size: 12px;
    color: #5a4a3a;
}
.next-week-events {
    font-size: 11px;
    color: #6a5a4a;
    margin-top: 4px;
}
.church-footer-info {
    font-size: 10px;
    color: #aaa;
    text-align: right;
}
</style>
"""


def render_bulletin(project_dir: Path):
    """2단 레이아웃으로 주보를 렌더링."""
    data = _load_bulletin_data(project_dir)
    if not data:
        st.warning("bulletin-data.yaml 파일을 찾을 수 없습니다.")
        return

    b = data.get("bulletin", {})
    if not b:
        st.warning("주보 데이터가 비어 있습니다.")
        return

    # ── 데이터 추출 ──
    church_name = b.get("church_name", "")
    # 한글 이름만 추출
    ko_name = church_name.split("(")[0].strip() if "(" in church_name else church_name
    en_name = church_name.split("(")[1].rstrip(")").strip() if "(" in church_name else ""

    date_str = b.get("date", "")
    if date_str:
        parts = date_str.split("-")
        date_display = f"{parts[0]}년 {int(parts[1])}월 {int(parts[2])}일 주일"
    else:
        date_display = ""

    issue = b.get("issue_number", "")
    issue_display = f"제 {issue}호"

    sermon = b.get("sermon", {})
    worship = b.get("worship_order", [])
    announcements = b.get("announcements", [])
    prayers = b.get("prayer_requests", [])
    celebrations = b.get("celebrations", {})
    offering = b.get("offering_team", [])
    next_week = b.get("next_week", {})

    # ── Worship Order 테이블 행 ──
    worship_rows = ""
    for w in worship:
        detail = w.get("detail") or ""
        performer = w.get("performer") or ""
        item_name = w.get("item", "")
        # 한글만 추출
        ko_item = item_name.split("(")[0].strip() if "(" in item_name else item_name
        ko_performer = performer.split("(")[0].strip() if "(" in performer else performer
        worship_rows += f"""
        <tr>
            <td class="worship-num">{w.get('order', '')}</td>
            <td>{ko_item}</td>
            <td>{detail}</td>
            <td>{ko_performer}</td>
        </tr>"""

    # ── Announcements HTML ──
    ann_html = ""
    for ann in announcements:
        title = ann.get("title", "")
        ko_title = title.split("(")[0].strip() if "(" in title else title
        content = ann.get("content", "")
        priority = ann.get("priority", "normal")
        badge = '<span class="announcement-badge">중요</span>' if priority == "high" else ""
        ann_html += f"""
        <div class="announcement-item">
            {badge}<span class="announcement-title">{ko_title}</span><br>
            {content}
        </div>"""

    # ── Prayer Requests HTML ──
    prayer_html = ""
    for pr in prayers:
        cat = pr.get("category", "")
        ko_cat = cat.split("(")[0].strip() if "(" in cat else cat
        content = pr.get("content", "")
        # 한국어 부분만
        ko_content = content.split("(")[0].strip() if "(" in content else content
        prayer_html += f"""
        <div class="prayer-item">
            <span class="prayer-category">{ko_cat}</span>: {ko_content}
        </div>"""

    # ── Celebrations HTML ──
    birthday_html = ""
    birthdays = celebrations.get("birthday", [])
    for bd in birthdays:
        birthday_html += f'<div class="celebration-item">{bd.get("name", "")} ({bd.get("date", "")})</div>'

    anniversary_html = ""
    anniversaries = celebrations.get("wedding_anniversary", [])
    for wa in anniversaries:
        names = wa.get("names", "")
        anniversary_html += f'<div class="celebration-item">{names} 가정 ({wa.get("date", "")})</div>'

    celebrations_section = ""
    if birthdays:
        celebrations_section += f"""
        <div class="section-header">생일 축하</div>
        {birthday_html}"""
    if anniversaries:
        celebrations_section += f"""
        <div class="section-header">결혼기념일 축하</div>
        {anniversary_html}"""

    # ── Offering Team ──
    offering_names = []
    for o in offering:
        ko_o = o.split("(")[0].strip() if "(" in o else o
        offering_names.append(ko_o)
    offering_display = " · ".join(offering_names)

    # ── Next Week ──
    nw_title = next_week.get("sermon_title", "")
    ko_nw_title = nw_title.split("(")[0].strip() if "(" in nw_title else nw_title
    nw_scripture = next_week.get("scripture", "")
    ko_nw_scripture = nw_scripture.split("(")[0].strip() if "(" in nw_scripture else nw_scripture
    nw_events = next_week.get("special_events", [])
    nw_events_html = ""
    for ev in nw_events:
        ko_ev = ev.split("(")[0].strip() if "(" in ev else ev
        nw_events_html += f"• {ko_ev}<br>"

    # ── Sermon ──
    sermon_title = sermon.get("title", "")
    ko_sermon_title = sermon_title.split("(")[0].strip() if "(" in sermon_title else sermon_title
    sermon_scripture = sermon.get("scripture", "")
    ko_sermon_scripture = sermon_scripture.split("(")[0].strip() if "(" in sermon_scripture else sermon_scripture
    sermon_series = sermon.get("series", "")
    ko_sermon_series = sermon_series.split("(")[0].strip() if "(" in sermon_series else sermon_series
    sermon_episode = sermon.get("series_episode", "")
    sermon_preacher = sermon.get("preacher", "")
    ko_preacher = sermon_preacher.split("(")[0].strip() if "(" in sermon_preacher else sermon_preacher

    series_display = ""
    if ko_sermon_series:
        series_display = f"{ko_sermon_series}"
        if sermon_episode:
            series_display += f" — 제 {sermon_episode}편"

    # ── Render ──
    html = _get_bulletin_css() + f"""
<div class="bulletin-container">

    <!-- Header -->
    <div class="bulletin-header">
        <div class="bulletin-church-name">{ko_name}</div>
        <div class="bulletin-subtitle">{en_name}</div>
        <div class="bulletin-date-bar">
            <span>{date_display}</span>
            <span>|</span>
            <span>{issue_display}</span>
        </div>
    </div>

    <!-- Sermon Banner -->
    <div class="sermon-banner">
        <div class="sermon-series">{series_display}</div>
        <div class="sermon-title">{ko_sermon_title}</div>
        <div class="sermon-scripture">본문: {ko_sermon_scripture}</div>
        <div class="sermon-preacher">설교: {ko_preacher}</div>
    </div>

    <!-- Two-Column Body -->
    <div class="bulletin-body">

        <!-- Left Column: Worship Order + Offering -->
        <div class="bulletin-col-left">
            <div class="section-header">예배 순서</div>
            <table class="worship-table">
                <thead>
                    <tr>
                        <th style="text-align:center">순</th>
                        <th>항목</th>
                        <th>내용</th>
                        <th>담당</th>
                    </tr>
                </thead>
                <tbody>
                    {worship_rows}
                </tbody>
            </table>

            <div class="section-header">헌금 봉사</div>
            <div class="offering-team">{offering_display}</div>

            {celebrations_section}
        </div>

        <!-- Right Column: Announcements + Prayer -->
        <div class="bulletin-col-right">
            <div class="section-header">공지사항</div>
            {ann_html}

            <div class="section-header">기도 제목</div>
            {prayer_html}
        </div>

    </div>

    <!-- Footer: Next Week -->
    <div class="bulletin-footer">
        <div class="next-week-box">
            <div class="next-week-label">▶ 다음 주 예고</div>
            <div class="next-week-title">{ko_nw_title}</div>
            <div class="next-week-scripture">본문: {ko_nw_scripture}</div>
            <div class="next-week-events">{nw_events_html}</div>
        </div>
        <div class="church-footer-info">
            {ko_name}<br>
            대한예수교장로회(PCK)
        </div>
    </div>

</div>
"""
    st.markdown(html, unsafe_allow_html=True)
