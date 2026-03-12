# 교회 행정 AI 에이전트 자동화 시스템

**한국 중소형 교회(100-500명)를 위한 AI 기반 행정 자동화 시스템.**

주보 제작, 새신자 관리, 재정 보고, 문서 발급, 일정 관리 등 반복적인 교회 행정 업무를 AI 에이전트가 자동 수행하여, 주당 23시간의 수동 행정 업무를 5시간 이하로 줄입니다.

> 이 시스템은 [AgenticWorkflow](soul.md) 프레임워크(부모)에서 태어난 **자식 시스템**입니다.
> 부모의 전체 DNA(절대 기준, 품질 보장, 안전장치, 기억 체계)를 구조적으로 내장합니다.

## 해결하는 문제

| 업무 | 주당 소요 시간 | 자동화 후 |
|------|-------------|---------|
| 주보 제작 | ~4시간 | ~15분 (AI 생성 + 1회 검토) |
| 새신자 등록·관리 | ~3시간 | ~30분 (파이프라인 자동화) |
| 재정 기록·보고 | ~6시간 | ~2시간 (이중 검토 유지) |
| 증명서·공문 발급 | ~3시간 | ~15분 (템플릿 기반 자동 생성) |
| 일정 관리 | ~2시간 | ~15분 (충돌 자동 감지) |
| 기타 데이터 정리 | ~5시간 | ~1시간 (자동 수집·검증) |
| **합계** | **~23시간** | **~4시간 15분** |

## 핵심 역량

| 역량 | 상세 |
|------|------|
| **5개 독립 워크플로우** | 주보 생성, 새신자 파이프라인, 월별 재정 보고, 문서 발급, 일정 관리 |
| **8개 전문 에이전트** | 각 데이터 파일에 대한 단독 쓰기 권한 — 데이터 충돌 원천 차단 |
| **29개 결정론적 검증 규칙** | P1 검증 스크립트 5개 (Members M1-M7, Finance F1-F7, Schedule S1-S6, Newcomers N1-N6, Bulletin B1-B3) |
| **한국어 자연어 인터페이스** | 41개 한국어 명령 패턴 → 8개 카테고리 + 대화형 시작 메뉴(`AskUserQuestion`) |
| **5개 Slash Commands** | `/start` (시작 메뉴), `/generate-bulletin` (주보), `/generate-finance-report` (재정), `/system-status` (건강 검사), `/validate-all` (검증) |
| **3계층 수신함 파이프라인** | Tier A: Excel/CSV, Tier B: Word/PDF, Tier C: 이미지 — 자동 파싱 + 신뢰도 점수 |
| **스캔-복제 엔진** | 7종 교회 문서(주보, 영수증, 순서지, 공문, 회의록, 증서, 초청장) 템플릿화 |
| **재정 안전 장치** | 재정 Autopilot 영구 비활성화 — 3중 강제(SOT + 에이전트 + 워크플로우) |
| **Hook 인프라** | 3개 Hook (PreToolUse 단독작성자 강제, PostToolUse YAML 검증, Setup 건강검사) — `.claude/settings.json` |
| **Streamlit 대시보드** | 비기술 사용자(행정 간사)를 위한 웹 UI — 기능 카드 클릭, 실시간 진행 표시, P1 독립 검증, HitL 승인 패널 |
| **한국 교회 용어 사전** | 50+ 용어(직분, 치리, 예배, 재정, 성례, 새신자, 문서) 정규화 |

## 빠른 시작

```bash
# 1. 저장소 클론
git clone https://github.com/idoforgod/AgenticWorkflow.git
cd AgenticWorkflow/church-admin

# 2. 인프라 검증 + Claude Code 실행
claude --init              # 사전 검증 (CA-1 ~ CA-8)
claude                     # 시스템 시작

# 3. "시작" 입력 → 대화형 메뉴 자동 표시
"시작"                      # → 상태 수집 + 환영 배너 + 대화형 메뉴

# 4. 또는 한국어로 직접 명령
"주보 만들어줘"              # 주보 생성
"새신자 등록"                # 새신자 파이프라인 시작
"이번 달 재정 보고서"         # 월별 재정 보고서

# 5. 또는 Streamlit 대시보드로 실행
streamlit run dashboard/app.py     # 웹 UI에서 모든 기능 사용
```

## 프로젝트 구조 (church-admin/)

```
church-admin/
├── CLAUDE.md                       # 시스템 지시서 (에이전트 로스터, SOT 규칙, 데이터 정책)
├── state.yaml                      # SOT — 시스템 전체 상태
├── data/                           # 6개 YAML 데이터 파일
│   ├── members.yaml                # 교인 명부 (HIGH — PII)
│   ├── finance.yaml                # 재정 기록 (HIGH — 금융)
│   ├── schedule.yaml               # 일정 (LOW)
│   ├── newcomers.yaml              # 새신자 (HIGH — PII)
│   ├── bulletin-data.yaml          # 주보 데이터 (LOW)
│   └── church-glossary.yaml        # 한국 교회 용어 사전 (LOW, append-only)
├── .claude/
│   ├── settings.json               # Hook 인프라
│   ├── agents/                     # 8개 전문 에이전트
│   ├── commands/                   # 5개 Slash Commands
│   ├── hooks/scripts/              # P1 검증 + 데이터 보호 Hook
│   └── skills/church-admin/        # 한국어 자연어 인터페이스 (41개 패턴)
├── scripts/                        # 파서, 검증, 유틸리티 스크립트
├── dashboard/                      # Streamlit 대시보드 (비기술 사용자용 웹 UI)
│   ├── app.py                      # 메인 앱 (기능 카드, 진행 표시, 결과 패널)
│   ├── engine/                     # 실행 엔진 (claude_runner, sot_watcher, context_builder, post_execution_validator)
│   └── components/                 # UI 컴포넌트 (status, progress, result, hitl_panel)
├── workflows/                      # 5개 독립 워크플로우 (영문 + 한국어)
├── templates/                      # 4개 문서 YAML 템플릿
├── inbox/                          # 3계층 파이프라인 수신함
├── docs/                           # 운영 가이드 (영문 + 한국어 쌍)
├── bulletins/                      # 생성된 주보 + 순서지
└── output/                         # 기타 출력물 (보고서, 증서, 공문)
```

## 데이터 민감도

| 민감도 | 데이터 파일 | 정책 |
|--------|-----------|------|
| **HIGH (PII)** | `members.yaml`, `newcomers.yaml` | `.gitignore` — 공개 금지, Soft-delete only |
| **HIGH (금융)** | `finance.yaml` | `.gitignore` — 공개 금지, Void-only 삭제 |
| LOW | `schedule.yaml`, `bulletin-data.yaml`, `church-glossary.yaml` | 버전 관리 |

## 유전받은 DNA

| DNA 구성 요소 | 교회 행정에서의 발현 |
|-------------|-----------------|
| **절대 기준** | 품질 절대주의 → 주보·재정 보고서 오류 제로 |
| **단일 파일 SOT** | `state.yaml` + 6개 데이터 파일, 각각 단독 쓰기 에이전트 |
| **4계층 품질 보장** | L0 Anti-Skip → L1 Verification → L1.5 pACS → L2 Adversarial Review |
| **P1 할루시네이션 봉쇄** | 5개 결정론적 검증 스크립트(29개 규칙) |
| **안전 Hook** | 단독작성자 강제, YAML 구문검증, 인프라 건강검사 |
| **Context Preservation** | 스냅샷 + Knowledge Archive + RLM 복원 |
| **대시보드 P1 봉쇄** | 대시보드가 LLM 밖에서 Python으로 직접 P1 검증 — 할루시네이션 원천봉쇄 |

## 구축 과정

14단계 워크플로우로 구축:

| 단계 | 내용 | 산출물 |
|------|------|--------|
| 1-2 | **Research** — 도메인 분석 + 문서 템플릿 분석 | 도메인 지식, 용어 사전, 템플릿 카탈로그 |
| 3 | 리서치 검토 (human gate) | 승인 |
| 4-5 | **Planning** — 데이터 스키마 설계 + 시스템 아키텍처 | 6개 스키마, 10개 에이전트 스펙 |
| 6 | 아키텍처 승인 (human gate) | 승인 |
| 7-9 | **Implementation M1** — 인프라 + P1 검증 + 핵심 기능 | 디렉터리, 시드 데이터, 검증 스크립트, 워크플로우 |
| 10 | M1 검토 (human gate) | 승인 |
| 11 | **Implementation M2** — 확장 기능 | 문서 발급, 일정 관리, 교단 지원 |
| 12-14 | 통합 테스트 + 문서화 + 최종 검수 | 15/15 PASS, IT 온보딩, 인수 완료 |

## 문서

| 문서 | 내용 |
|------|------|
| [`CHURCH-ADMIN-README.md`](CHURCH-ADMIN-README.md) | 시스템 개요, 핵심 역량, 빠른 시작 |
| [`CHURCH-ADMIN-ARCHITECTURE-AND-PHILOSOPHY.md`](CHURCH-ADMIN-ARCHITECTURE-AND-PHILOSOPHY.md) | 설계 철학, 아키텍처, 데이터·에이전트·안전 구조 |
| [`CHURCH-ADMIN-USER-MANUAL.md`](CHURCH-ADMIN-USER-MANUAL.md) | 시스템 관리자(IT 자원봉사자) 운영·유지보수 |
| [`church-admin/docs/`](church-admin/docs/) | 최종 사용자 운영 가이드 (빠른 시작, 사용법, 문제 해결) |

> `AGENTICWORKFLOW-*.md` = **프레임워크/방법론** 문서, `CHURCH-ADMIN-*.md` = **도메인 특화 시스템** 문서

---

## AgenticWorkflow 프레임워크 기반

이 시스템은 AgenticWorkflow 만능줄기세포(Pluripotent Stem Cell) 프레임워크에서 분화되었습니다. 아래는 부모 프레임워크의 방법론과 인프라입니다.

### 프로젝트 목표

```
Phase 1: 워크플로우 설계  →  workflow.md (설계도)
Phase 2: 워크플로우 구현  →  실제 동작하는 시스템 (최종 산출물)
```

워크플로우를 만드는 것은 중간 산출물입니다. **워크플로우에 기술된 내용이 실제로 동작하는 것**이 최종 목표입니다.

### 워크플로우 구조

모든 워크플로우는 3단계로 구성됩니다:

1. **Research** — 정보 수집 및 분석
2. **Planning** — 계획 수립, 구조화, 사람의 검토/승인
3. **Implementation** — 실제 실행 및 산출물 생성

### 저장소 구조

```
AgenticWorkflow/
├── CLAUDE.md              # Claude Code 전용 지시서
├── AGENTS.md              # 모든 AI 에이전트 공통 지시서
├── AGENTICWORKFLOW-USER-MANUAL.md              # 프레임워크 사용자 매뉴얼
├── AGENTICWORKFLOW-ARCHITECTURE-AND-PHILOSOPHY.md  # 프레임워크 설계 철학 및 아키텍처
├── CHURCH-ADMIN-README.md                      # 교회 행정 시스템 개요
├── CHURCH-ADMIN-ARCHITECTURE-AND-PHILOSOPHY.md # 교회 행정 시스템 아키텍처
├── CHURCH-ADMIN-USER-MANUAL.md                 # 교회 행정 시스템 관리자 매뉴얼
├── DECISION-LOG.md            # 프로젝트 설계 결정 로그 (ADR)
├── COPYRIGHT.md              # 저작권
├── soul.md                   # 프로젝트 영혼 (자식 시스템에 유전되는 DNA 정의)
├── .claude/
│   ├── settings.json      # Hook 설정 (Setup + SessionEnd)
│   ├── commands/           # Slash Commands (/install, /maintenance)
│   ├── hooks/scripts/     # 21개 Python 스크립트 (Context Preservation 6 + Safety 3 + P1 Validation 10 + Setup 2)
│   ├── context-snapshots/ # 런타임 스냅샷 (gitignored)
│   └── skills/
│       ├── workflow-generator/ # 워크플로우 설계·생성 스킬
│       └── doctoral-writing/   # 박사급 학술 글쓰기 스킬
├── church-admin/           # 교회 행정 시스템 (자식 — 빌드 산출물)
│   ├── CLAUDE.md           # 시스템 지시서 (에이전트 로스터, SOT, 데이터 정책)
│   ├── state.yaml          # SOT (시스템 전체 상태)
│   ├── data/               # 6개 YAML 데이터 파일
│   ├── .claude/agents/     # 8개 전문 에이전트
│   ├── scripts/            # 파서, 검증, 백업 스크립트
│   ├── dashboard/          # Streamlit 대시보드 (웹 UI + P1 독립 검증 엔진)
│   ├── workflows/          # 5개 독립 워크플로우
│   ├── templates/          # 문서 YAML 템플릿
│   ├── inbox/              # 3계층 파이프라인 수신함
│   └── docs/               # 운영 가이드 (영문 + 한국어)
├── prompt/                 # 프롬프트 자료
└── coding-resource/        # 이론적 기반 자료
    └── recursive language models.pdf
```

### 스킬

| 스킬 | 설명 |
|------|------|
| **workflow-generator** | Research → Planning → Implementation 3단계 구조의 `workflow.md`를 설계·생성. Sub-agents, Agent Teams, Hooks, Skills를 조합한 구현 설계 포함. |
| **doctoral-writing** | 박사급 학위 논문의 학문적 엄밀성과 명료성을 갖춘 글쓰기 지원. 한국어·영어 모두 지원. |

### Context Preservation System

컨텍스트 토큰 초과, `/clear`, 컨텍스트 압축 시 작업 내역이 상실되는 것을 방지하는 자동 저장·복원 시스템입니다. 5개의 Hook 스크립트가 작업 내역을 MD 파일로 자동 저장하고, 새 세션 시작 시 RLM 패턴(포인터 + 요약 + 완료 상태 + Git 상태)으로 이전 맥락을 복원합니다. Knowledge Archive에는 세션별 phase(단계), phase_flow(다단계 전환 흐름), primary_language(주요 언어), error_patterns(Error Taxonomy 12패턴 분류 + resolution 매칭), tool_sequence(RLE 압축 도구 시퀀스), final_status(세션 종료 상태), tags(경로 기반 검색 태그), session_duration_entries(세션 길이) 메타데이터가 자동 기록됩니다. 스냅샷의 설계 결정은 품질 태그 우선순위로 정렬되어 노이즈가 제거되고, 스냅샷 압축 시 IMMORTAL 섹션이 우선 보존되며(압축 감사 추적 포함), 모든 파일 쓰기에 atomic write(temp → rename) 패턴이 적용됩니다. P1 할루시네이션 봉쇄로 KI 스키마 검증, 부분 실패 격리, SOT 쓰기 패턴 검증, SOT 스키마 검증이 결정론적으로 수행됩니다.

| 스크립트 | 트리거 | 역할 |
|---------|--------|------|
| `context_guard.py` | (Hook 디스패처) | Hook 통합 진입점. `--mode`에 따라 적절한 스크립트로 라우팅 |
| `save_context.py` | SessionEnd, PreCompact | 전체 스냅샷 저장 |
| `restore_context.py` | SessionStart | 포인터+요약으로 복원 |
| `update_work_log.py` | PostToolUse | 9개 도구(Edit, Write, Bash, Task, NotebookEdit, TeamCreate, SendMessage, TaskCreate, TaskUpdate) 작업 로그 누적, 75% threshold 시 자동 저장 |
| `generate_context_summary.py` | Stop | 매 응답 후 증분 스냅샷 + Knowledge Archive 아카이빙 (30초 throttling, E5 Guard) |
| `_context_lib.py` | (공유 라이브러리) | 파싱, 생성, SOT 캡처, 토큰 추정, Smart Throttling, Autopilot 상태 읽기·검증, ULW 감지·준수 검증, 절삭 상수 중앙화(10개), sot_paths() 경로 통합, 다단계 전환 감지, 결정 품질 태그 정렬, Error Taxonomy 12패턴 분류+Resolution 매칭, IMMORTAL-aware 압축+감사 추적, E5 Guard 중앙화, Knowledge Archive 통합(부분 실패 격리), KI 스키마 검증, SOT 스키마 검증, Adversarial Review P1 검증, Translation P1 검증, pACS P1 검증, Cross-Step Traceability P1 검증, Domain Knowledge P1 검증, Predictive Debugging P1, Abductive Diagnosis Layer(사전 증거 수집 + 사후 검증 + KA 아카이빙 + Fast-Path) |
| `setup_init.py` | Setup (`--init`) | 세션 시작 전 인프라 건강 검증 (Python, PyYAML, 스크립트 구문, 디렉터리) + SOT 쓰기 패턴 검증(P1 할루시네이션 봉쇄) |
| `setup_maintenance.py` | Setup (`--maintenance`) | 주기적 건강 검진 (stale archives, knowledge-index 무결성, work_log 크기, doc-code 동기화 검증(DC-1~DC-4)) |
| `block_destructive_commands.py` | PreToolUse (Bash) | 위험 명령 실행 전 차단 (git push --force, git reset --hard, rm -rf / 등). exit code 2 + stderr 피드백 (P1 할루시네이션 봉쇄) |
| `block_test_file_edit.py` | PreToolUse (Edit\|Write) | TDD 모드(`.tdd-guard` 존재) 시 테스트 파일 수정 차단. exit code 2 + stderr 피드백 |
| `predictive_debug_guard.py` | PreToolUse (Edit\|Write) | 에러 이력 기반 위험 파일 사전 경고. `risk-scores.json` 캐시 조회 → 임계값 초과 시 stderr 경고 (exit code 0, 경고 전용) |
| `diagnose_context.py` | (독립 스크립트) | Abductive Diagnosis 사전 증거 수집 — 품질 게이트 FAIL 시 증거 번들(retry history, upstream evidence, hypothesis priority) 수집. Orchestrator가 수동 호출 |
| `validate_diagnosis.py` | (독립 스크립트) | Abductive Diagnosis P1 사후 검증 — AD1-AD10 구조적 무결성 검증. Orchestrator가 수동 호출 |

### Autopilot Mode

워크플로우를 무중단으로 실행하는 모드입니다. `(human)` 단계를 품질 극대화 기본값으로 자동 승인하고, `(hook)` exit code 2는 그대로 차단합니다.

- **Anti-Skip Guard**: 각 단계 완료 시 산출물 파일 존재 + 최소 크기(100 bytes) 검증
- **Decision Log**: 자동 승인 결정은 `autopilot-logs/step-N-decision.md`에 기록
- **런타임 강화**: Hook 기반 컨텍스트 주입 + 스냅샷 내 Autopilot 상태 보존

상세: `AGENTS.md §5.1`

### ULW (Ultrawork) Mode

프롬프트에 `ulw`를 포함하면 활성화되는 **철저함 강도(thoroughness intensity) 오버레이**입니다. Autopilot(자동화 축)과 **직교**하여 어떤 조합이든 가능합니다.

- **I-1. Sisyphus Persistence**: 최대 3회 재시도, 각 시도는 다른 접근법. 100% 완료 또는 불가 사유 보고
- **I-2. Mandatory Task Decomposition**: TaskCreate → TaskUpdate → TaskList 필수
- **I-3. Bounded Retry Escalation**: 동일 대상 3회 초과 재시도 금지(품질 게이트는 별도 예산 적용)
- **Compliance Guard**: Python Hook이 3개 강화 규칙의 준수를 결정론적으로 검증 (스냅샷 IMMORTAL 보존)

상세: `CLAUDE.md` ULW Mode 섹션

### 4계층 품질 보장 (Quality Assurance Stack)

워크플로우 각 단계의 산출물이 **기능적 목표를 100% 달성했는지** 검증하는 다계층 품질 보장 시스템입니다.

| 계층 | 이름 | 검증 대상 | 성격 |
|------|------|---------|------|
| **L0** | Anti-Skip Guard | 파일 존재 + ≥ 100 bytes | 결정론적 (Hook) |
| **L1** | Verification Gate | 기능적 목표 100% 달성 | 의미론적 (Agent 자기검증) |
| **L1.5** | pACS Self-Rating | F/C/L 3차원 신뢰도 | Pre-mortem Protocol 기반 |
| **L2** | Adversarial Review (Enhanced) | 적대적 검토 (`@reviewer` + `@fact-checker`) | `Review:` 필드 지정 단계 |

- **검증 기준 선행 선언**: 워크플로우의 각 단계에 `Verification` 필드로 구체적·측정 가능한 기준을 Task 앞에 정의
- **pACS (predicted Agent Confidence Score)**: Pre-mortem Protocol 후 F(Factual Grounding), C(Completeness), L(Logical Coherence) 채점. min-score 원칙: pACS = min(F,C,L)
- **행동 트리거**: GREEN(≥70) 자동 진행, YELLOW(50-69) 플래그 후 진행, RED(<50) 재작업
- **Adversarial Review (L2)**: `@reviewer`(코드/산출물 비판적 분석) + `@fact-checker`(외부 사실 검증) Sub-agent로 독립적 검토. P1 검증(`validate_review.py`)으로 리뷰 품질 보장
- **Team 3계층 검증**: L1(Teammate 자기검증) + L1.5(pACS 자기채점) + L2(Team Lead 종합검증 + 단계 pACS)
- **검증 로그**: `verification-logs/step-N-verify.md`, `pacs-logs/step-N-pacs.md`
- **Abductive Diagnosis**: 품질 게이트(Verification/pACS/Review) FAIL → 재시도 사이에 3단계 구조화된 진단(P1 사전 증거 수집 → LLM 원인 분석 → P1 사후 검증) 수행. Fast-Path(FP1-FP3)로 결정론적 단축 가능
- **하위 호환**: `Verification` 필드 없는 기존 워크플로우는 Anti-Skip Guard만으로 동작

상세: `AGENTS.md §5.3`, `§5.4`, `§5.5`, `§5.6`

### 절대 기준

이 프로젝트의 모든 설계·구현 의사결정에 적용되는 최상위 규칙:

1. **품질 최우선** — 속도, 비용, 작업량보다 최종 결과물의 품질이 유일한 기준
2. **단일 파일 SOT** — Single Source of Truth + 계층적 메모리 구조로 데이터 일관성 보장
3. **코드 변경 프로토콜 (CCP)** — 코드 변경 전 의도 파악 → 영향 범위 분석 → 변경 설계 3단계 수행. 분석 깊이는 변경 규모에 비례. **코딩 기준점(CAP-1~4)**: 코딩 전 사고, 단순성 우선, 목표 기반 실행, 외과적 변경
4. **품질 > SOT, CCP** — 세 기준이 충돌하면 품질이 우선. SOT와 CCP는 수단이지 목적이 아님

### 이론적 기반

`coding-resource/recursive language models.pdf` — 장기기억(long-term memory) 구현에 필수적인 이론을 담은 논문입니다. 에이전트가 세션을 넘어 지식을 축적하고 활용하는 메커니즘의 이론적 토대입니다.

### AI 도구 호환성

이 프로젝트는 **Hub-and-Spoke 패턴**으로 모든 AI CLI 도구에서 동일한 방법론이 자동 적용됩니다.

**Hub (방법론 SOT):**

| 파일 | 역할 |
|------|------|
| `AGENTS.md` | 모든 AI 도구 공통 — 절대 기준, 설계 원칙, 워크플로우 구조 정의 |

**Spoke (도구별 확장):**

| AI CLI 도구 | 시스템 프롬프트 파일 | 자동 적용 |
|------------|-------------------|----------|
| Claude Code | `CLAUDE.md` | Yes |
| Gemini CLI | `GEMINI.md` + `.gemini/settings.json` | Yes |
| Codex CLI | `AGENTS.md` (직접 읽음) | Yes |
| Copilot CLI | `.github/copilot-instructions.md` | Yes |
| Cursor | `.cursor/rules/agenticworkflow.mdc` | Yes |

모든 Spoke 파일의 절대 기준과 설계 원칙은 `AGENTS.md`와 동일합니다. 차이는 도구별 구현 매핑의 구체성뿐입니다.

## 문서 읽기 순서

### 교회 행정 시스템 문서

| 순서 | 문서 | 목적 |
|------|------|------|
| 1 | **README.md** (이 파일) | 시스템 전체 개요 파악 |
| 2 | [`CHURCH-ADMIN-ARCHITECTURE-AND-PHILOSOPHY.md`](CHURCH-ADMIN-ARCHITECTURE-AND-PHILOSOPHY.md) | 설계 철학과 아키텍처 이해 |
| 3 | [`CHURCH-ADMIN-USER-MANUAL.md`](CHURCH-ADMIN-USER-MANUAL.md) | 시스템 관리자(IT 자원봉사자) 운영·유지보수 |
| 4 | [`church-admin/docs/`](church-admin/docs/) | 최종 사용자 운영 가이드 (빠른 시작, 사용법, 문제 해결) |

### 프레임워크 (부모) 문서

| 순서 | 문서 | 목적 |
|------|------|------|
| 1 | **README.md** (이 파일) | 프로젝트 전체 개요 파악 |
| 1.5 | [`soul.md`](soul.md) | 프로젝트 영혼 — 규칙 아래의 이유, DNA 유전 철학 |
| 2 | [`AGENTICWORKFLOW-ARCHITECTURE-AND-PHILOSOPHY.md`](AGENTICWORKFLOW-ARCHITECTURE-AND-PHILOSOPHY.md) | 프레임워크 설계 철학과 아키텍처 이해 |
| 2.5 | [`DECISION-LOG.md`](DECISION-LOG.md) | 모든 설계 결정의 맥락과 근거 추적 |
| 3 | [`AGENTICWORKFLOW-USER-MANUAL.md`](AGENTICWORKFLOW-USER-MANUAL.md) | 프레임워크 사용법 학습 |
| 4 | `AGENTS.md` / `CLAUDE.md` | 사용하는 AI 도구에 맞는 지시서 참조 |

> **`AGENTICWORKFLOW-*.md`** = 프레임워크/방법론 문서, **`CHURCH-ADMIN-*.md`** = 도메인 시스템 문서
