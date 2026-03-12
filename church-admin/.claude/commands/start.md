---
description: "교회 행정 시스템 시작 — 실행 모드 선택 + 대화형 안내"
---

Display the execution mode selection, then guide the user into the chosen mode.

## MANDATORY EXECUTION RULE

**This command MUST be executed when the user types ANY of these patterns.** Do not skip, summarize, or shortcut — run all steps in order.

Trigger patterns:
- "시작", "시작하자", "시작해줘", "시작합니다"
- "워크플로우 시작", "워크플로우를 시작하자", "작업을 시작하자"
- "start", "let's start", "begin", "get started"
- "뭐 할 수 있어?", "뭘 할 수 있어?", "가능한 기능"
- "메뉴", "메뉴 보여줘", "메뉴판"
- "도움말", "사용법", "어떻게 해?", "어떻게 사용해?"
- "처음", "처음부터", "다시 시작"
- Or simply enters a greeting without a specific task

---

## Step 1 — Run Smart Router (MANDATORY FIRST ACTION)

**Before doing ANYTHING else**, run the smart router script:

```bash
python3 scripts/start_router.py --state state.yaml
```

This script (P1 deterministic):
- Checks `state.yaml` validity
- Checks Streamlit installation + version
- Checks `dashboard/app.py` and `scripts/show_menu.py` existence
- Returns JSON with `raw` data + `display` blocks (pre-formatted text)

### Fallback — If start_router.py fails

If the script produces no output, throws an error, or returns invalid JSON:
- **Skip mode selection entirely**
- **Proceed directly to Step 4-CLI** (run `show_menu.py` → feature menu)
- This preserves 100% of existing functionality as fallback

## Step 2 — Display Welcome Banner (P1 — VERBATIM)

Display the `display.welcome_banner` value from the JSON output **exactly as-is**.
Do NOT modify, reformat, add to, or reinterpret the banner text.

## Step 3 — Mode Selection (P1 — VERBATIM options)

Use `AskUserQuestion` with:
- **Question text**: Use `display.mode_question` value exactly
- **Options**: Use `display.mode_options` array exactly — each item has `label` and `description`

Do NOT add options that are not in the `display.mode_options` array.
Do NOT modify the `label` or `description` text.

## Step 4 — Route Based on Mode Selection

### If "대화형 모드 (CLI)" selected → Step 5-CLI

Proceed to the CLI feature menu flow below (Step 5-CLI through Step 8-CLI).

### If "대시보드 모드 (Web UI)" selected → Dashboard Instructions

Check `raw.modes[1].available` in the JSON:

- **If `available: true`**: Display `display.dashboard_instructions` **exactly as-is** (P1 — VERBATIM). Do NOT modify paths, commands, or warning text.
- **If `available: false`**: Display `display.dashboard_unavailable` **exactly as-is** (P1 — VERBATIM).

After displaying dashboard instructions, show:
```
다른 작업을 하시겠습니까? "시작"을 입력하시면 메뉴로 돌아갑니다.
```

### If "Other" (free text) selected

Route through SKILL.md intent mapping.

---

## CLI Mode Flow (Steps 5-CLI through 8-CLI)

These steps execute ONLY when the user selects "대화형 모드 (CLI)".
This is the existing feature menu flow, preserved exactly.

### Step 5-CLI — Run Menu Script

```bash
python3 scripts/show_menu.py --state state.yaml --data-dir data/
```

This script:
- Reads `state.yaml` for current system state
- Reads all data files for live counts
- Detects pending alerts (overdue follow-ups, missing bulletins, missing reports)
- Returns JSON with: status summary, prioritized alerts, ordered menu items

**IMPORTANT**: The script output is the SOLE source of truth for menu content. Do NOT manually read data files to compute status — the script already does this deterministically.

### Step 6-CLI — Display Status + Alerts (from show_menu.py output)

Using the JSON output from Step 5-CLI, display:

```
현재 상태:
  교인: {status.members.total}명 (활동 {status.members.active}명)
  새신자: {status.newcomers.active}명 관리 중
  최근 주보: 제 {status.bulletin.last_issue}호 ({status.bulletin.last_date})
  데이터 무결성: {status.validation.total_passed}/{status.validation.total_checks} 통과
```

If `alerts` array is non-empty, show each alert:
```
주의사항:
  !! {alerts[0].message_ko}
  !! {alerts[1].message_ko}
```

### Step 7-CLI — Show Feature Menu (AskUserQuestion — 2-Page Structure)

AskUserQuestion allows max 4 options. The JSON output provides `menu_page1` (top 3 items) and `menu_page2` (remaining items). Use the 4th slot for "더보기" to access page 2.

#### Page 1 (Initial Menu)

Use `AskUserQuestion` with the 3 items from `menu_page1` + "더보기" option:

For each menu item:
- `label`: Use `label_ko` value
- `description`: Use `desc_ko` value. If item has an `alert` field, prepend it: `"!! {alert} — {desc_ko}"`

The question text: "어떤 작업을 도와드릴까요?"

**Example** (actual values come from script JSON):
```
Question: "어떤 작업을 도와드릴까요?"
Options:
  1. 새신자 (Newcomers) — "!! 새신자 3명 후속 관리 필요 — 새신자 현황을 확인하고 관리합니다"
  2. 재정 (Finance) — "!! 2026-01 재정 보고서 미생성 — 헌금/지출 내역을 확인하고 보고서를 만듭니다"
  3. 주보 (Bulletin) — "이번 주 주보를 만들거나 확인합니다"
  4. 더보기... — "일정, 문서 발급, 교인 관리, 시스템 관리 등 추가 메뉴"
```

The user can also select "Other" to describe what they need in free text.

#### Page 2 (When "더보기" Selected)

Show a second AskUserQuestion with the items from `menu_page2`:

```
Question: "추가 메뉴에서 선택해주세요."
Options: (from menu_page2, up to 4 items)
  1. 교인 관리 (Members) — "교인 검색, 등록, 수정을 합니다"
  2. 일정 (Schedule) — "이번 주 일정과 행사를 확인합니다"
  3. 문서 발급 (Documents) — "증명서, 공문 등을 발급합니다"
  4. 시스템 관리 (System) — "데이터 검증, 상태 확인을 합니다"
```

### Step 8-CLI — Route Based on Feature Selection

After the user selects an option, execute the corresponding action:

| Selection | Action |
|-----------|--------|
| 주보 (Bulletin) | Read `data/bulletin-data.yaml` → show current bulletin status → offer sub-menu: 생성/미리보기/수정 |
| 새신자 (Newcomers) | Read `data/newcomers.yaml` → show stage dashboard → offer sub-menu: 등록/현황/단계변경 |
| 교인 관리 (Members) | Ask for sub-action via AskUserQuestion: 검색/등록/수정/통계 |
| 재정 (Finance) | Read `data/finance.yaml` → show this month summary → offer sub-menu: 보고서/내역/영수증 |
| 일정 (Schedule) | Read `data/schedule.yaml` → show this week → offer sub-menu: 확인/등록/예약 |
| 문서 발급 (Documents) | Ask for document type via AskUserQuestion: 증명서/이명증서/공문/회의록 |
| 시스템 관리 (System) | Run `python3 scripts/validate_all.py` → show results in Korean |
| Other (free text) | Route through SKILL.md intent mapping |

---

## Step 9 — After Action Completion

After completing any action, show completion message and offer to return:

```
작업이 완료되었습니다.
다른 작업을 하시겠습니까? "시작"을 입력하시면 메뉴로 돌아갑니다.
```

---

## P1 Hallucination Prevention Rules (MANDATORY)

`start_router.py`의 JSON `display` 블록은 **수정 없이 그대로 출력**한다:
- `display.welcome_banner` → VERBATIM 출력 (숫자, 교회명, 상태 텍스트 변경 금지)
- `display.mode_options` → AskUserQuestion options에 VERBATIM 사용 (옵션 추가/제거/수정 금지)
- `display.dashboard_instructions` → VERBATIM 출력 (경로, 명령어, 경고문 변경 금지)
- `display.dashboard_unavailable` → VERBATIM 출력 (설치 명령어 변경 금지)

**절대 금지**:
- `display` 블록의 숫자, 경로, 명령어를 재해석하거나 변형하는 행위
- `display` 블록에 없는 내용을 추가하는 행위
- `display.mode_options`에 없는 선택지를 AskUserQuestion에 추가하는 행위

---

## Response Style

- **Language**: Korean (존댓말 — formal polite speech)
- **Tone**: Warm, helpful, patient (as if guiding a first-time user)
- **Format**: Clean, visual, with status indicators
- **Never assume** the user knows technical terms — translate system concepts to church terminology
- **Never show** raw file paths or technical error messages — translate to friendly Korean

## Important Rules

- Run `start_router.py` FIRST — this is non-negotiable (Step 1)
- In CLI mode, run `show_menu.py` FIRST — this is non-negotiable (Step 5-CLI)
- Use `AskUserQuestion` tool for all menus — do NOT just print a menu and wait for text input
- Finance-related actions always require human confirmation (autopilot disabled for finance)
- If `start_router.py` fails, fall back to CLI mode (Step 5-CLI onwards)
- If `show_menu.py` fails, fall back to reading state.yaml manually + show static menu
- The menu adapts dynamically based on alerts and enabled features
