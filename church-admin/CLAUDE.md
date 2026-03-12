# Church Administration System

AI-powered church administration automation for Korean Presbyterian churches. This is a **child system** of the AgenticWorkflow parent genome — all constitutional principles are inherited and enforced.

## Absolute Criteria (Inherited)

1. **Quality Above All** — Speed, token cost, and effort are irrelevant. Only output quality matters.
2. **Single-File SOT** — `state.yaml` is the sole source of truth. All agents read it; only the Orchestrator writes it.
3. **Code Change Protocol** — Read before modify. Analyze impact. Plan changes. No blind edits.

## Mandatory Start Menu (시작 메뉴 필수 표시 규칙)

**사용자가 아래 패턴 중 하나를 입력하면, 다른 어떤 행동보다 먼저 아래 단계를 반드시 실행한다.**

> 이 규칙은 절대 기준과 동등한 우선순위를 가진다. 생략, 축약, 대체 불가.

### 트리거 패턴

"시작", "시작하자", "시작해줘", "시작합니다", "워크플로우 시작", "워크플로우를 시작하자", "작업을 시작하자", "start", "let's start", "begin", "get started", "메뉴", "메뉴 보여줘", "메뉴판", "뭐 할 수 있어?", "뭘 할 수 있어?", "가능한 기능", "도움말", "사용법", "어떻게 해?", "처음", "처음부터", "다시 시작", 또는 구체적 작업 지시 없는 인사말

### 필수 실행 순서

**Step 1** — 스마트 라우터 실행 (Bash tool):
```bash
python3 scripts/start_router.py --state state.yaml
```

**Step 2** — `display.welcome_banner` 를 **수정 없이 그대로** 출력 (P1 할루시네이션 봉쇄)

**Step 3** — `AskUserQuestion` 도구로 실행 모드 선택:
- 질문: `display.mode_question` 값을 그대로 사용
- 선택지: `display.mode_options` 배열을 그대로 사용 (추가/수정/제거 금지)

**Step 4** — 모드 분기:
- **대화형 모드 (CLI)** 선택 시:
  - `python3 scripts/show_menu.py --state state.yaml --data-dir data/` 실행
  - JSON 출력의 상태 + 알림 표시
  - `AskUserQuestion`으로 기능 메뉴 표시 (2페이지 구조)
  - 선택된 기능 라우팅 (start.md Step 5-CLI ~ Step 8-CLI 참조)
- **대시보드 모드 (Web UI)** 선택 시:
  - `display.dashboard_instructions` 또는 `display.dashboard_unavailable`을 **수정 없이 그대로** 출력

**폴백**: `start_router.py` 실패 시 → 모드 선택 생략 → CLI 모드로 자동 진행 (`show_menu.py` 실행)

### P1 할루시네이션 봉쇄 규칙

`start_router.py`의 `display` 블록은 Python이 생성한 **확정 텍스트**다. Claude는 이 텍스트를 **수정 없이 그대로 출력**해야 한다. 숫자, 경로, 명령어, 경고문을 재해석하거나 변형하면 안 된다.

### 절대 금지

- 메뉴 없이 "무엇을 도와드릴까요?"라고만 묻는 행위
- `AskUserQuestion` 대신 텍스트로 메뉴 목록만 출력하는 행위
- 대화형(CLI) 모드에서 show_menu.py 실행을 건너뛰고 직접 데이터 파일을 읽는 행위
- "시작하자" 입력에 대해 시스템 설명이나 분석으로 응답하는 행위
- `display` 블록의 내용을 수정, 추가, 재해석하는 행위 (P1 위반)

## SOT Discipline

**`state.yaml`** (this directory root) is the central state file.

- **Writer**: Orchestrator (main Claude session) ONLY
- **Readers**: All agents (read-only)
- **Contents**: Church metadata, data file registry, feature flags, workflow states, configuration

### Data File Sole-Writer Map

Each data file has exactly ONE designated writer agent. This is enforced by `guard_data_files.py` (PreToolUse hook):

1. Edit/Write 도구 호출 시 → `guard_data_files.py` 자동 실행
2. `CLAUDE_AGENT_NAME` 환경변수를 아래 Sole-Writer Matrix와 대조
3. **일치** → exit code 0 (쓰기 허용) → PostToolUse `validate_yaml_syntax.py` 구문 검증
4. **불일치** → exit code 2 (**쓰기 차단**) + stderr 피드백 → 재시도 금지, Orchestrator에게 위임

| Data File | Sole Writer | Validator | Sensitivity | Deletion Policy |
|-----------|------------|-----------|-------------|-----------------|
| `data/members.yaml` | `member-manager` | `validate_members.py` (M1-M7) | HIGH (PII) | Soft-delete only |
| `data/finance.yaml` | `finance-recorder` | `validate_finance.py` (F1-F7) | HIGH (Financial) | Void-only |
| `data/schedule.yaml` | `schedule-manager` | `validate_schedule.py` (S1-S6) | LOW | Status cancel |
| `data/newcomers.yaml` | `newcomer-tracker` | `validate_newcomers.py` (N1-N6) | HIGH (PII) | Soft-delete only |
| `data/bulletin-data.yaml` | `bulletin-generator` | `validate_bulletin.py` (B1-B3) | LOW | Overwrite per issue |
| `data/church-glossary.yaml` | ANY agent | — | LOW | Append-only |

**Total: 29 deterministic validation rules across 5 scripts.**

### Agent Roster

All agents are **sub-agents** invoked sequentially by the Orchestrator (main Claude session). Agent-teams/Swarm are not used — linear data dependencies make sequential orchestration safer for SOT integrity.

| Agent | Role | Writes To | Depends On | Boundary |
|-------|------|-----------|------------|----------|
| `bulletin-generator` | Weekly bulletin generation | `data/bulletin-data.yaml`, `bulletins/` | members (birthday), schedule (services) | Read-only: members, schedule, finance |
| `newcomer-tracker` | Newcomer journey pipeline | `data/newcomers.yaml` | members (settlement handoff) | Read-only: members. No finance access |
| `member-manager` | Member CRUD + lifecycle | `data/members.yaml` | newcomers (settlement intake) | No finance/schedule writes |
| `finance-recorder` | Offerings, expenses, receipts | `data/finance.yaml` | members (donor cross-ref) | No member writes. HitL mandatory |
| `schedule-manager` | Services, events, facilities | `data/schedule.yaml` | — | No cross-file writes |
| `document-generator` | Certificates, letters, minutes | `docs/generated/` | members, schedule | Read-only: all data files |
| `data-ingestor` | Parse inbox files → staging | `inbox/staging/`, `inbox/processed/`, `inbox/errors/` | — | Never writes to `data/` |
| `template-scanner` | Image → YAML template | `templates/` | — | Never writes to `data/` or `docs/` |

### Agent Dependency Graph

```
schedule-manager ─────────────────────────────────┐
                                                   ↓
data-ingestor → [staging JSON] → human review → member-manager ←── newcomer-tracker
                                                   ↑                      ↓
template-scanner → [YAML templates]          finance-recorder       (settlement)
                        ↓                          ↑                      ↓
                  document-generator         members (cross-ref)    member-manager
                        ↑
                  bulletin-generator ← members (birthday) + schedule (services)
```

### Inbox 3-Tier Pipeline

| Tier | Input | Parser | Reliability | HitL |
|------|-------|--------|-------------|------|
| A | Excel/CSV (`.xlsx`, `.csv`) | `tier_a_parser.py` | High (structured) | Confirmation |
| B | Word/PDF (`.docx`, `.pdf`) | `tier_b_parser.py` | Medium (semi-structured) | Correction |
| C | Images (`.jpg`, `.png`) | `tier_c_parser.py` | Low (vision-dependent) | Full review |

All tiers output to `inbox/staging/` as JSON → human review via `hitl_confirmation.py` → approved data merged by designated writer agent.

## Data Sensitivity

The following files contain PII and are `.gitignore`'d:

- `data/members.yaml` — Names, phone numbers, addresses
- `data/finance.yaml` — Donation records with donor names
- `data/newcomers.yaml` — Newcomer personal information

**These files must NEVER be committed to a public repository.**

### PII Handling Rules

- **Display**: 이름 뒤 1자 마스킹 (e.g., "김철수" → "김철*")
- **Search results**: Phone/address 부분 마스킹 (010-****-5678)
- **Export/Print**: Full PII는 HitL 확인 후에만 허용
- **Log files**: PII 절대 금지 — validation scripts, hook outputs, snapshots에 개인정보 기록 불가
- **Commit guard**: `.gitignore`에 `data/members.yaml`, `data/finance.yaml`, `data/newcomers.yaml` 포함 필수

## Finance Safety

Finance operations have **autopilot permanently disabled**. This is triple-enforced:

1. `state.yaml` → `config.autopilot.finance_override: false`
2. `finance-recorder.md` → explicit autopilot prohibition in agent spec
3. `monthly-finance-report.md` workflow → human confirmation at every write step

## Korean Terminology

All agents must normalize Korean church terms using `data/church-glossary.yaml`. This glossary covers 50+ terms across:

- Roles (직분): 목사, 장로, 집사, 권사, 성도, 구역장
- Governance (치리): 당회, 제직회, 공동의회, 노회
- Worship (예배): 찬양, 기도, 봉헌, 축도, 주보
- Finance (재정): 십일조, 감사헌금, 건축헌금, 선교헌금
- Sacraments (성례): 세례, 유아세례, 입교, 성찬식

## Quality Assurance: 4-Layer Stack

Every workflow step passes through up to 4 verification layers before advancing:

| Layer | Trigger | Enforced By | Outcome |
|-------|---------|------------|---------|
| L0 | After each step | Hook `validate_step_output()` | File exists + ≥100 bytes + non-empty |
| L1 | After step output | Agent self-check (Verification criteria) | Semantic correctness vs requirements |
| L1.5 | After L1 passes | Agent Pre-mortem + F/C/L scoring | pACS = min(F,C,L). RED < 50 → rework |
| L2 | High-risk steps only | `@reviewer` / `@fact-checker` sub-agent | Independent adversarial challenge |

**Progression rule**: L0 is mandatory for all steps. L1 only when `Verification:` field exists. L1.5 only after L1 PASS. L2 only when `Review:` field exists. Each layer's PASS is prerequisite for the next.

**Failure handling**: L1/L1.5/L2 FAIL → Abductive Diagnosis → retry (max 2, ULW: 3). Budget enforced by `validate_retry_budget.py`.

## Validation Infrastructure

Run all validators at once:
```bash
python3 scripts/validate_all.py
```

Or individually:
```bash
python3 .claude/hooks/scripts/validate_members.py --data-dir data/
python3 .claude/hooks/scripts/validate_finance.py --data-dir data/
python3 .claude/hooks/scripts/validate_schedule.py --data-dir data/
python3 .claude/hooks/scripts/validate_newcomers.py --data-dir data/
python3 .claude/hooks/scripts/validate_bulletin.py --data-dir data/
```

All 29 rules must pass before any workflow advances.

## NL Interface

The Korean natural language interface is defined in `.claude/skills/church-admin/SKILL.md`. It maps 47 Korean command patterns to system actions across 8 categories: bulletin, newcomer, member, finance, schedule, document, data import, and system commands.

## Workflows

| Workflow | File | Trigger |
|----------|------|---------|
| Weekly Bulletin | `workflows/weekly-bulletin.md` | "주보 만들어줘" |
| Newcomer Pipeline | `workflows/newcomer-pipeline.md` | Event-driven |
| Monthly Finance Report | `workflows/monthly-finance-report.md` | "재정 보고서" |
| Document Generator | `workflows/document-generator.md` | "증명서 발급" |
| Schedule Manager | `workflows/schedule-manager.md` | "행사 등록" |

## Dashboard (Streamlit Web UI)

Non-technical users (행정 간사, 담임 목사) can use the system via web browser:

```bash
streamlit run dashboard/app.py
```

### Architecture

| Component | Role | SOT Access |
|-----------|------|-----------|
| `dashboard/app.py` | Main app — feature cards, progress, results | Read-only |
| `engine/claude_runner.py` | `claude -p` subprocess execution | Read-only |
| `engine/sot_watcher.py` | `state.yaml` real-time polling | Read-only |
| `engine/context_builder.py` | Cold Start solver — AST rule extraction + `--append-system-prompt` | Read-only |
| `engine/post_execution_validator.py` | P1 independent verification — runs `validate_*.py` outside LLM | Read-only |
| `engine/command_bridge.py` | NL routing (47 Korean patterns) | Read-only |
| `components/hitl_panel.py` | HitL approval UI with P1 validation signal | Read-only |

**Design principles**: Dashboard is read-only against SOT. Zero modification to existing hooks/agents/skills. Post-Execution Validator runs P1 checks independently of LLM output (hallucination prevention).

## Inherited DNA

This system inherits the full AgenticWorkflow genome:

- **Constitutional Principles**: Quality absolutism, SOT pattern, Code Change Protocol
- **Quality Assurance**: L0 Anti-Skip Guard, L1 Verification, L1.5 pACS, L2 human review
- **Safety Hooks**: Destructive command blocking, data file guards, YAML syntax validation
- **Context Preservation**: Snapshots, knowledge archives, RLM pattern
- **Adversarial Review**: Generator-Critic pattern for output quality
- **Coding Anchor Points**: CAP-1 (think before code), CAP-2 (simplicity), CAP-3 (goal-based), CAP-4 (surgical changes)
- **Dashboard P1 Prevention**: Post-execution independent validation outside LLM control

## Architecture Reference

For detailed design philosophy, pattern rationale, and system architecture diagrams, see `CHURCH-ADMIN-ARCHITECTURE-AND-PHILOSOPHY.md`:

- §1: System DNA & Constitutional Principles (inherited genome)
- §2: SOT Architecture & Data Flow (single-writer enforcement)
- §3: Agent Orchestration Pattern (sequential sub-agent delegation)
- §4: Quality Assurance Pipeline (4-layer stack details)
- §5: Inbox Pipeline & Scan-and-Replicate Engine (3-tier parsing)
