# publish-plan 스킬 설계서

> **날짜:** 2026-04-24
> **상태:** Draft
> **관련:** publish-write 개선 (기획 단계 추가)

---

## 1. 배경 및 문제

현재 `/publish-write` 스킬은 "목차 받고 바로 집필"로 진입한다. 실제 출간에 필수적인 기획 단계가 전혀 없어서:

- 책의 컨셉, 독자, 핵심 메시지에 대한 고민 없이 집필 시작
- 목차 자동 제안도 wiki _index.md 스캔 수준에 그침
- 챕터별 구성이 사전에 설계되지 않아 집필 중 방향이 흔들릴 수 있음

## 2. 목표

1. **새 스킬 `/publish-plan`** 을 만들어 기획 전 과정을 담당
2. LLM이 **소크라테스식 인터뷰**로 저자와 함께 기획을 구체화
3. KB(위키)를 인터뷰 과정에 자연스럽게 활용
4. 기획안을 **독립 엔티티**로 CRUD 관리 (저장/불러오기/수정/재개)
5. 기획 확정 시 project로 변환하여 `/publish-write`와 연동
6. `/publish-write`는 기획 완료 상태에서 집필에만 집중하도록 개선

## 3. 스킬 구조

### 3.1 publish-plan (신규)

별도 스킬로 분리. 기획만 독립 실행 가능.

### 3.2 publish-write (변경)

기존 Step 1(프로젝트 유형 + 목차 확인)과 "KB 기반 목차 자동 제안" 로직을 publish-plan으로 이관. publish-write는 확정된 project.yaml 기반으로 집필만 수행.

**publish-write 변경사항:**

| 현재 | 변경 후 |
|------|---------|
| Step 1: 프로젝트 유형 + 목차 확인 | 제거 → publish-plan으로 이관 |
| "목차 없으면 KB 기반 자동 제안" | 제거 → publish-plan의 structure 단계로 이관 |
| project.yaml 직접 생성 | 제거 → publish-plan finalize에서 생성 |
| Step 2: 프로젝트 초기화 | 제거 (이미 finalize에서 완료) |
| Step 3~7: 프로필 로드 → 집필 → 저장 | 유지 |

**publish-write 새로운 시작 흐름:**

```
1. projects/ 스캔 → 프로젝트 선택
2. 프로젝트 없으면 → "/publish-plan을 먼저 실행하세요" 안내
3. project.yaml 로드 + proposal.md 로드 (있으면, ~1-2K 토큰)
4. 저자 프로필 로드
5. 챕터별 집필 시작 (기존 Step 4~7)
```

proposal.md는 집필 시 전체 방향과 맥락을 상기하는 용도로 활용. 챕터 작업 중 토큰이 부족해지면 proposal.md 요약만 유지하고 원문은 해제한다.

---

## 4. 기획안 데이터 구조

### 4.1 디렉토리 구조

```
{workspace}/
└── plans/
    └── plan_{id}/                  # id: 사용자 지정 또는 자동 생성
        ├── plan.yaml               # 기획 상태 + 구조화 데이터 (LLM용)
        ├── proposal.md             # 기획서 문서 (사람용)
        └── interview_log.md        # 소크라테스 인터뷰 누적 기록
```

### 4.2 plan.yaml 스키마

```yaml
id: "은혜론_2026"
title: "무조건적 은혜 - 은혜의 재발견"
type: new_book                      # new_book / revision / sermon_collection / commentary
author_id: "pastor_kim"
created: 2026-04-24
updated: 2026-04-24
status: concept                     # concept / audience / message / structure / detail / finalized

# 소크라테스 인터뷰 진행 상태
interview:
  current_phase: concept            # concept / audience / message / structure / detail
  completed_phases: []
  next_question_context: ""         # 재개 시 LLM이 참조할 맥락 요약

# 기획 내용 (인터뷰 진행에 따라 점진적으로 채워짐)
concept:
  motivation: ""                    # 왜 이 책을 쓰는가
  core_question: ""                 # 이 책이 답하려는 질문
  working_title: ""                 # 가제

audience:
  primary: ""                       # 주 독자층
  prior_knowledge: ""               # 독자의 사전 지식 수준
  reader_outcome: ""                # 독자가 얻어갈 것

message:
  thesis: ""                        # 핵심 주장/메시지
  key_themes: []                    # 핵심 주제 목록
  theological_stance: ""            # 신학적 방향 (theology.yaml 기반)

structure:
  total_chapters: 0
  estimated_length: ""              # 예상 총 분량
  flow_type: ""                     # 논리 전개 방식 (연역/귀납/내러티브 등)

outline:                            # 챕터별 상세 (유형에 따라 깊이 다름)
  - chapter: 1
    title: ""
    core_argument: ""               # 핵심 논지
    sections: []                    # new_book: 섹션 구조 / sermon_collection: 빈칸
    kb_sources: []                  # 참조할 wiki 기사
    estimated_length: ""
    notes: ""                       # 인터뷰 중 나온 메모

# 기획 확정 시 project 변환 정보
finalized:
  project_name: ""                  # projects/{name}으로 변환될 이름
  finalized_date: ""
```

### 4.3 interview_log.md 형식

```markdown
# 인터뷰 기록 - {title}

## Phase: concept (2026-04-24)

**Q:** 이 책을 쓰려는 동기가 무엇인가요?
**A:** 설교를 하면서 은혜에 대한 오해가 많다는 걸 느꼈습니다...

**Q:** KB를 보니 은혜 관련 설교가 12편 있는데, 가장 핵심적인 메시지가 뭐였나요?
**A:** ...

---

## Phase: audience (2026-04-24)
...
```

### 4.4 proposal.md 형식

인터뷰 진행에 따라 자동 갱신되는 사람이 읽기 좋은 기획서.

```markdown
# {title}

## 기획 의도
{concept.motivation}
{concept.core_question}

## 대상 독자
{audience.primary}
{audience.prior_knowledge}
{audience.reader_outcome}

## 핵심 메시지
{message.thesis}
{message.key_themes}

## 목차 구성

### 1장: {title}
- 핵심 논지: {core_argument}
- 구성: {sections}
- 참조 자료: {kb_sources}
- 예상 분량: {estimated_length}
...
```

---

## 5. 소크라테스 인터뷰 워크플로우

### 5.1 5단계 골격

```
concept → audience → message → structure → detail
```

각 단계는 순서가 있지만, 저자가 원하면 자유롭게 이동 가능. "목차부터 생각해봤어"라면 structure로 점프하고 나중에 concept을 채울 수 있음.

### 5.2 단계별 역할

| Phase | 핵심 질문 | KB 활용 | 산출물 |
|-------|----------|---------|--------|
| **concept** | 왜 이 책을 쓰는가? 어떤 질문에 답하는가? | KB 현황 간략 제시 ("이 주제로 설교 N편, 개념 기사 M개") | motivation, core_question, working_title |
| **audience** | 누가 읽는가? 독자가 뭘 얻어가는가? | 저자의 기존 청중 패턴 참조 (sermon_pattern.yaml) | primary, prior_knowledge, reader_outcome |
| **message** | 이 책의 핵심 주장은? | KB에서 저자의 신학적 입장 끌어옴 (theology.yaml + concepts/) | thesis, key_themes, theological_stance |
| **structure** | 몇 장? 어떤 흐름? | KB 기사 클러스터 분석으로 목차 후보 제안 | total_chapters, flow_type, outline 초안 |
| **detail** | 각 챕터에서 뭘 말하는가? | 챕터별 관련 KB 기사 매칭 | outline 상세화 (유형별 깊이 조절) |

### 5.3 유형별 인터뷰 깊이 조절

**new_book:**
- concept: 깊이 파고듦 (백지 상태이므로)
- audience: 상세히
- message: 상세히
- structure: 상세히
- detail: B 수준 (섹션 구조까지)

**sermon_collection:**
- concept: 가벼움 ("어떤 설교들을 모을까?")
- audience: 간략
- message: 전체 설교집의 메시지 방향
- structure: 배치 순서와 전체 흐름 중심
- detail: A 수준 (설교 자체 구조 보존)

**commentary:**
- concept: 범위 확정 중심 ("어떤 본문?")
- audience: 간략
- message: 접근 방향과 신학적 강조점
- structure: 본문 단위가 이미 구조를 결정
- detail: 본문 단위별 접근 방향

**revision:**
- concept: "왜 개정하는가?" 중심
- audience: 기존 독자 vs 새 독자
- message: 변경된 강조점
- structure: 원본 구조 대비 변경 방향
- detail: 변경/보완 포인트 중심

### 5.4 status와 phase의 관계

`plan.yaml`의 `status`는 `interview.current_phase`와 동기화된다. phase가 전환되면 status도 함께 변경.

```
current_phase: concept    → status: concept
current_phase: audience   → status: audience
current_phase: message    → status: message
current_phase: structure  → status: structure
current_phase: detail     → status: detail
finalize 실행 시          → status: finalized
```

### 5.5 인터뷰 진행 규칙

1. **한 번에 한 질문** - 여러 질문을 한꺼번에 던지지 않음
2. **KB 기반 제안** - 초반에 KB 현황을 간략히 보여주고, 대화 중 적절한 시점에 "KB를 보니 ~인데, 이런 방향은 어떠세요?" 식으로 자료를 대화에 자연스럽게 녹임
3. **저자의 답변 존중** - LLM이 방향을 주도하지 않음. 질문으로 저자가 스스로 발견하도록 유도
4. **단계 완료 판단** - 해당 phase의 plan.yaml 필드가 충분히 채워지면 다음 단계 제안 (강제 아님)
5. **매 단계 완료 시 자동 저장** - plan.yaml + proposal.md + interview_log.md 갱신
6. **중단/재개** - 언제든 "여기까지 하자" → 현재 상태 저장, 다음 세션에서 plan.yaml 로드하여 이어감

### 5.6 KB 활용 방식

인터뷰 중 KB를 세 가지 시점에 활용한다:

**시점 1: 인터뷰 시작 시 (concept phase)**
- 사용자가 주제를 언급하면 관련 KB 현황을 간략히 제시
- "이 주제로 설교 N편, 개념 기사 M개가 KB에 있습니다"
- 저자가 자신의 축적된 자료를 인식하고 기획에 활용하도록 도움

**시점 2: 대화 중 적절한 시점**
- 저자의 답변에서 키워드를 추출하여 관련 KB 기사 검색
- "KB에서 '무조건적 은혜'에 대한 기사를 보면, 선생님이 이전에 ~라고 하셨는데..."
- 저자가 자신의 과거 저술/설교와 일관성을 유지하도록 도움

**시점 3: structure/detail phase**
- KB 기사 클러스터 분석으로 목차 후보 제안
- 챕터별 관련 KB 기사 매칭
- "이 챕터에서 활용할 수 있는 자료가 wiki에 N개 있습니다"

KB 검색은 기존 search-strategy.md의 계층적 검색 (Level 0 → 1 → 2)을 따른다.

---

## 6. CRUD 인터페이스

### 6.1 트리거 및 동작 모드

```
/publish-plan                     → 기획안 목록 + 새로 만들기/이어하기 선택
/publish-plan new                 → 새 기획안 시작
/publish-plan {plan_id}           → 기존 기획안 이어하기
/publish-plan list                → 기획안 목록 + 상태 요약
/publish-plan delete {plan_id}    → 기획안 삭제 (확인 후)
/publish-plan finalize {plan_id}  → 기획안 확정 → project로 변환
```

**plan_id 규칙:** 사용자가 지정하는 짧은 식별자 (예: `은혜론_2026`, `로마서강해`). 디렉토리명은 `plans/plan_{id}/`이지만, 사용자는 항상 bare id만 사용한다. sanitize 규칙: 공백 → `_`, 특수문자 제거, 한글·영문·숫자·언더스코어만 허용.

### 6.2 기획안 목록 표시

```
기획안 목록

ID               유형               상태           마지막 작업
--------------------------------------------------------------
은혜론_2026      new_book          detail         2026-04-24
로마서강해       commentary        audience       2026-04-23
설교모음_1       sermon_collection finalized      2026-04-20

[new] 새 기획안 시작  |  기획안 ID를 입력하면 이어서 작업합니다
```

### 6.3 재개 시 흐름

```
1. plan.yaml 로드
2. interview.current_phase, completed_phases, next_question_context 확인
3. interview_log.md 로드 (이전 대화 맥락 파악)
4. proposal.md 로드 (현재까지의 기획 상태 파악)
5. "지난번에 {phase} 단계까지 진행했습니다. {next_question_context} 이어서 진행할까요?"
6. 인터뷰 재개
```

### 6.4 finalize 흐름

기획 확정 시:

```
plans/plan_{id}/
    ├── plan.yaml (status: finalized)
    ├── proposal.md
    └── interview_log.md
         ↓
projects/{project_name}/ 생성
    ├── project.yaml    ← plan.yaml의 outline + 메타데이터 변환
    ├── proposal.md     ← plans/에서 복사 (원본도 유지)
    ├── drafts/
    ├── reviews/
    └── exports/
```

**변환 매핑:**

| plan.yaml | project.yaml |
|-----------|-------------|
| id | plan_id (참조용) |
| title | name |
| type | type |
| author_id | author_id |
| concept + audience + message | summary (요약 필드, 신규) |
| structure.flow_type | flow_type (신규) |
| outline | outline (draft_file, slug 자동 생성) |
| finalized.project_name | (디렉토리명) |

**project.yaml 스키마 추가 필드:**

```yaml
# 기존 필드에 추가
plan_id: ""                         # 원본 기획안 ID (plans/plan_{id}/ 참조)
summary:                            # publish-plan에서 생성된 기획 요약
  motivation: ""                    # concept.motivation
  core_question: ""                 # concept.core_question
  audience: ""                      # audience.primary + reader_outcome
  thesis: ""                        # message.thesis
  key_themes: []                    # message.key_themes
flow_type: ""                       # structure.flow_type
```

기존 project.yaml에 이 필드들이 없는 경우(이전 버전 호환) 빈 값으로 취급한다. publish-write는 summary가 있으면 집필 맥락으로 활용하고, 없으면 기존 방식대로 진행한다.

원본 `plans/plan_{id}/`는 아카이브로 보존.

---

## 7. 컨텍스트 관리

### 7.1 인터뷰 시 토큰 예산

소크라테스 인터뷰는 대화 중심이므로 KB 로드를 최소화한다.

- 저자 프로필 4파일: ~2K 토큰 (상시 유지)
- KB 검색 결과: Level 0~1 위주, 필요 시만 Level 2. 한 번에 10K 토큰 이하
- interview_log.md: 재개 시 전체 로드하되, 길어지면 최근 phase + 요약만 로드
- plan.yaml: ~1K 토큰 (상시 유지)

### 7.2 interview_log.md가 길어질 때

interview_log.md 파일 자체는 항상 전체 내용을 보존한다. 컨텍스트 로드 시에만 축약 적용:

500줄 초과 시 **컨텍스트 로드 전략:**
1. 파일 원본은 변경하지 않음 (전체 기록 보존)
2. 컨텍스트에는 현재 phase의 전체 대화만 로드
3. 이전 phase는 plan.yaml에 이미 구조화된 결과가 있으므로 별도 로드 불필요
4. plan.yaml의 next_question_context가 핵심 맥락을 담아 연속성 보장

---

## 8. publish-setup 변경사항

워크스페이스 초기화 시 `plans/` 디렉토리를 추가 생성해야 한다.

```
{workspace}/
├── plans/              ← 신규 추가
├── authors/
├── wiki/
├── raw/
├── projects/
├── snapshots/
└── logs/
```

**기존 워크스페이스 호환:** publish-plan이 트리거될 때 `plans/` 디렉토리가 없으면 자동 생성한다. 기존 워크스페이스 사용자가 publish-setup을 다시 실행할 필요 없음.

---

## 9. 영향 받는 스킬 목록

| 스킬 | 변경 유형 | 내용 |
|------|----------|------|
| publish-plan | **신규** | 소크라테스 인터뷰 기반 기획 스킬 |
| publish-write | **수정** | Step 1~2 제거, project 선택으로 시작 |
| publish-setup | **수정** | plans/ 디렉토리 추가 생성 |
| shared/references/workspace-schema.md | **수정** | plans/ 구조 + plan.yaml 스키마 추가 |

---

## 10. 파일 변경 요약

### 신규 생성
- `skills/publish-plan/SKILL.md` - 기획 스킬 본체
- `skills/publish-plan/references/interview-guide.md` - 단계별 인터뷰 질문 가이드 + 유형별 깊이 조절 규칙

### 수정
- `skills/publish-write/SKILL.md` - Step 1~2 제거, project 선택으로 시작점 변경
- `skills/publish-write/references/writing-modes.md` - 목차 관련 로직 제거 (publish-plan으로 이관)
- `skills/publish-setup/SKILL.md` - plans/ 디렉토리 생성 추가
- `skills/shared/references/workspace-schema.md` - plans/ 구조 + plan.yaml 스키마 + project.yaml 신규 필드(plan_id, summary, flow_type) 추가
- `skills/shared/references/context-management.md` - plan 스킬 토큰 예산 추가
- `CLAUDE.md` - 스킬 목록에 publish-plan 추가
- `docs/specs/2026-04-21-publish-agent-design.md` - 스킬 목록 및 파이프라인 다이어그램에 publish-plan 추가

### 커스텀 파일 패턴
- `skills/publish-plan/references/custom-interview-guide.md` - 사용자별 인터뷰 질문/단계 커스터마이징 (있으면 interview-guide.md에 추가 적용)
