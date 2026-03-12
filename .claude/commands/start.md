---
description: "교회 행정 시스템 시작 — 스마트 라우터 → 모드 선택 → 대화형/대시보드 안내"
---

Church Admin 시스템을 시작합니다. 스마트 라우터를 실행하고, 실행 모드를 안내합니다.

## MANDATORY EXECUTION RULE

**이 명령은 아래 패턴이 입력되면 다른 모든 행동보다 먼저 실행한다.** 컨텍스트 복원, 세션 분석, 시스템 설명 등 어떤 작업도 이 흐름보다 우선할 수 없다.

트리거 패턴:
- "시작", "시작하자", "시작해줘", "시작합니다"
- "워크플로우 시작", "워크플로우를 시작하자", "작업을 시작하자"
- "start", "let's start", "begin", "get started"
- "뭐 할 수 있어?", "뭘 할 수 있어?", "가능한 기능"
- "메뉴", "메뉴 보여줘", "메뉴판"
- "도움말", "사용법", "어떻게 해?", "어떻게 사용해?"
- "처음", "처음부터", "다시 시작"
- 또는 구체적 작업 지시 없는 인사말

**우선순위**: 이 라우팅은 컨텍스트 복원(CONTEXT RECOVERY)보다 우선한다. 세션 시작 직후에도 "시작하자"가 입력되면 반드시 이 흐름을 실행한다.

---

## Step 1 — 스마트 라우터 실행 (MANDATORY FIRST ACTION)

**다른 어떤 행동보다 먼저**, 스마트 라우터 스크립트를 실행한다:

```bash
cd church-admin && python3 scripts/start_router.py --state state.yaml
```

> 부모 디렉터리(AgenticWorkflow/)에서 실행하므로 `cd church-admin &&` 프리픽스가 필수.

이 스크립트 (P1 결정론적):
- `state.yaml` 유효성 확인
- Streamlit 설치 + 버전 확인
- `dashboard/app.py`와 `scripts/show_menu.py` 존재 확인
- JSON으로 `raw` 데이터 + `display` 블록 (사전 포맷된 텍스트) 반환

### 폴백 — start_router.py 실패 시

스크립트가 출력 없음, 오류, 유효하지 않은 JSON을 반환하면:
- **모드 선택을 건너뛰고**
- **Step 4-CLI로 직접 진행** (`show_menu.py` 실행 → 기능 메뉴)
- 기존 기능 100%를 폴백으로 보존

## Step 2 — 환영 배너 표시 (P1 — VERBATIM)

JSON 출력의 `display.welcome_banner` 값을 **수정 없이 그대로** 출력한다.
배너 텍스트를 수정, 재포맷, 추가, 재해석하지 않는다.

## Step 3 — 모드 선택 (P1 — VERBATIM 선택지)

`AskUserQuestion` 도구로:
- **질문**: `display.mode_question` 값을 그대로 사용
- **선택지**: `display.mode_options` 배열을 그대로 사용 — 각 항목의 `label`과 `description`

`display.mode_options` 배열에 없는 선택지를 추가하지 않는다.
`label`이나 `description` 텍스트를 수정하지 않는다.

## Step 4 — 모드 분기

### "대화형 모드 (CLI)" 선택 시 → Step 5-CLI

아래 CLI 기능 메뉴 흐름으로 진행한다 (Step 5-CLI ~ Step 8-CLI).

### "대시보드 모드 (Web UI)" 선택 시 → 대시보드 안내

JSON의 `raw.modes[1].available` 확인:

- **`available: true`**: `display.dashboard_instructions`를 **수정 없이 그대로** 출력 (P1 — VERBATIM). 경로, 명령어, 경고문을 수정하지 않는다.
- **`available: false`**: `display.dashboard_unavailable`를 **수정 없이 그대로** 출력 (P1 — VERBATIM).

대시보드 안내 후:
```
다른 작업을 하시겠습니까? "시작"을 입력하시면 메뉴로 돌아갑니다.
```

### "Other" (자유 텍스트) 선택 시

church-admin SKILL.md 인텐트 매핑으로 라우팅한다.

---

## CLI 모드 흐름 (Steps 5-CLI ~ 8-CLI)

사용자가 "대화형 모드 (CLI)"를 선택했을 때만 실행한다.

### Step 5-CLI — 메뉴 스크립트 실행

```bash
cd church-admin && python3 scripts/show_menu.py --state state.yaml --data-dir data/
```

이 스크립트:
- `state.yaml`에서 현재 시스템 상태 읽기
- 모든 데이터 파일에서 실시간 카운트 읽기
- 긴급 알림 감지 (후속 관리 필요, 누락된 주보, 누락된 보고서)
- JSON으로 반환: 상태 요약, 우선순위 알림, 정렬된 메뉴 항목

**중요**: 스크립트 출력이 메뉴 콘텐츠의 유일한 진실 소스. 상태 계산을 위해 데이터 파일을 직접 읽지 않는다.

### Step 6-CLI — 상태 + 알림 표시

Step 5-CLI의 JSON 출력을 사용하여 표시:

```
현재 상태:
  교인: {status.members.total}명 (활동 {status.members.active}명)
  새신자: {status.newcomers.active}명 관리 중
  최근 주보: 제 {status.bulletin.last_issue}호 ({status.bulletin.last_date})
  데이터 무결성: {status.validation.total_passed}/{status.validation.total_checks} 통과
```

`alerts` 배열이 비어있지 않으면 각 알림 표시:
```
주의사항:
  !! {alerts[0].message_ko}
  !! {alerts[1].message_ko}
```

### Step 7-CLI — 기능 메뉴 (AskUserQuestion — 2페이지 구조)

AskUserQuestion은 최대 4개 선택지. JSON의 `menu_page1` (상위 3개) + "더보기"로 페이지 2 접근.

#### 페이지 1 (초기 메뉴)

`menu_page1`의 3개 항목 + "더보기" 선택지로 `AskUserQuestion` 사용:

각 메뉴 항목:
- `label`: `label_ko` 값 사용
- `description`: `desc_ko` 값 사용. `alert` 필드가 있으면 앞에 추가: `"!! {alert} — {desc_ko}"`

질문: "어떤 작업을 도와드릴까요?"

#### 페이지 2 ("더보기" 선택 시)

`menu_page2` 항목으로 두 번째 `AskUserQuestion`:

질문: "추가 메뉴에서 선택해주세요."

### Step 8-CLI — 기능 라우팅

| 선택 | 동작 |
|------|------|
| 주보 (Bulletin) | `data/bulletin-data.yaml` 읽기 → 현재 주보 상태 → 하위 메뉴: 생성/미리보기/수정 |
| 새신자 (Newcomers) | `data/newcomers.yaml` 읽기 → 단계 대시보드 → 하위 메뉴: 등록/현황/단계변경 |
| 교인 관리 (Members) | AskUserQuestion으로 하위 동작: 검색/등록/수정/통계 |
| 재정 (Finance) | `data/finance.yaml` 읽기 → 이번 달 요약 → 하위 메뉴: 보고서/내역/영수증 |
| 일정 (Schedule) | `data/schedule.yaml` 읽기 → 이번 주 → 하위 메뉴: 확인/등록/예약 |
| 문서 발급 (Documents) | AskUserQuestion으로 문서 유형: 증명서/이명증서/공문/회의록 |
| 시스템 관리 (System) | `python3 scripts/validate_all.py` 실행 → 한국어 결과 표시 |
| Other (자유 텍스트) | SKILL.md 인텐트 매핑으로 라우팅 |

> **경로 규칙**: 모든 파일 경로는 `church-admin/` 프리픽스를 붙여야 한다. 부모 디렉터리에서 실행하므로 `church-admin/data/members.yaml` 형태.

---

## Step 9 — 작업 완료 후

```
작업이 완료되었습니다.
다른 작업을 하시겠습니까? "시작"을 입력하시면 메뉴로 돌아갑니다.
```

---

## P1 할루시네이션 봉쇄 규칙 (MANDATORY)

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

## 응답 스타일

- **언어**: Korean (존댓말 — formal polite speech)
- **톤**: 따뜻하고 친절하며 인내심 있게 (처음 사용하는 분을 안내하듯)
- **포맷**: 깔끔하고 시각적으로, 상태 표시자 포함
- **원칙**: 기술 용어를 교회 용어로 번역하여 안내
