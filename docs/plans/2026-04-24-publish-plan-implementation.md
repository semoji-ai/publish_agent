# publish-plan 스킬 구현 계획

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 소크라테스식 인터뷰 기반 `/publish-plan` 스킬을 만들고, `/publish-write`를 기획 완료 상태에서만 집필하도록 개선한다.

**Architecture:** 새 스킬 SKILL.md + 참조 문서 생성, 기존 스킬/공유 참조 수정. 코드 없이 순수 마크다운 워크플로우 정의.

**Tech Stack:** Markdown skills (SKILL.md), YAML schemas

**Spec:** `docs/specs/2026-04-24-publish-plan-design.md`

---

## File Structure

### 신규 생성
- `skills/publish-plan/SKILL.md` — 기획 스킬 본체 (CRUD + 소크라테스 인터뷰 + finalize)
- `skills/publish-plan/references/interview-guide.md` — 5단계 인터뷰 질문 가이드 + 유형별 깊이 조절

### 수정
- `skills/shared/references/workspace-schema.md` — plans/ 디렉토리 + plan.yaml 스키마 + project.yaml 신규 필드 추가
- `skills/shared/references/context-management.md` — plan 스킬 토큰 예산 행 추가
- `skills/publish-setup/SKILL.md` — Step 3에 plans/ 디렉토리 추가
- `skills/publish-write/SKILL.md` — Step 1~2 제거, project 선택 시작으로 변경
- `skills/publish-write/references/writing-modes.md` — 목차 관련 로직 제거
- `CLAUDE.md` — 스킬 목록에 publish-plan 추가
- `docs/specs/2026-04-21-publish-agent-design.md` — 스킬 테이블 + 파이프라인 다이어그램 갱신

---

## Chunk 1: 공유 참조 문서 수정

기존 공유 참조 문서에 publish-plan 관련 스키마와 구조를 추가한다.

### Task 1: workspace-schema.md에 plans/ 구조 추가

**Files:**
- Modify: `skills/shared/references/workspace-schema.md:12-73` (디렉토리 트리)
- Modify: `skills/shared/references/workspace-schema.md:194-249` (project.yaml 스키마)

- [ ] **Step 1: 디렉토리 트리에 plans/ 추가**

`skills/shared/references/workspace-schema.md`의 디렉토리 트리(12-73행)에서 `projects/` 앞에 `plans/` 항목을 삽입한다:

```
├── plans/                         # 기획안 저장소 (/publish-plan이 관리)
│   └── plan_{id}/                 # 기획안별 디렉토리 (id: 사용자 지정)
│       ├── plan.yaml              # 기획 상태 + 구조화 데이터 (스키마 → 4.8)
│       ├── proposal.md            # 기획서 문서 (사람용, 인터뷰 진행 시 자동 갱신)
│       └── interview_log.md       # 소크라테스 인터뷰 누적 기록
```

- [ ] **Step 2: plan.yaml 스키마 섹션 추가**

`workspace-schema.md` 끝(raw entry 스키마 뒤)에 새 섹션 `## 4.8 plan.yaml 스키마`를 추가한다. 스펙 문서 섹션 4.2의 전체 YAML 스키마를 포함:

```markdown
## 4.8 plan.yaml 스키마

`plans/plan_{id}/plan.yaml`에 위치. `/publish-plan` 스킬이 생성·관리한다.

{스펙 섹션 4.2의 전체 YAML 스키마 복사}

**status 흐름:** `concept` → `audience` → `message` → `structure` → `detail` → `finalized`

- `status`는 `interview.current_phase`와 동기화된다
- finalize 실행 시 `status: finalized`로 변경되며 project로 변환 가능

**plan_id 규칙:**
- 사용자가 지정하는 짧은 식별자 (예: `은혜론_2026`, `로마서강해`)
- 디렉토리명: `plans/plan_{id}/`
- sanitize: 공백 → `_`, 특수문자 제거, 한글·영문·숫자·언더스코어만 허용
```

- [ ] **Step 3: project.yaml 스키마에 신규 필드 추가**

`workspace-schema.md`의 project.yaml 스키마(194-249행) YAML 블록 내 `wiki_queries:` 뒤에 다음 필드를 추가:

```yaml
plan_id: ""                         # 원본 기획안 ID (plans/plan_{id}/ 참조). 기획 없이 생성된 경우 빈 문자열
summary:                            # publish-plan에서 생성된 기획 요약 (finalize 시 자동 생성)
  motivation: ""                    # 왜 이 책을 쓰는가
  core_question: ""                 # 이 책이 답하려는 질문
  audience: ""                      # 주 독자층 + 독자가 얻어갈 것
  thesis: ""                        # 핵심 주장/메시지
  key_themes: []                    # 핵심 주제 목록
flow_type: ""                       # 논리 전개 방식 (연역/귀납/내러티브 등)
```

그리고 필드 설명에 추가:
- `plan_id`: publish-plan의 finalize로 생성된 경우 원본 기획안 ID. 기획 없이 생성된 기존 프로젝트는 빈 문자열.
- `summary`: 기획 요약. 없으면 빈 값으로 취급 (하위 호환).
- `flow_type`: 기획에서 결정된 전개 방식. 없으면 빈 문자열 (하위 호환).

- [ ] **Step 4: 검증**

파일을 읽어서 확인:
- 디렉토리 트리에 plans/ 포함
- plan.yaml 스키마 섹션(4.8) 존재
- project.yaml에 plan_id, summary, flow_type 필드 존재

- [ ] **Step 5: 커밋**

```bash
git add skills/shared/references/workspace-schema.md
git commit -m "feat: add plans/ structure and plan.yaml schema to workspace-schema"
```

### Task 2: context-management.md에 plan 스킬 토큰 예산 추가

**Files:**
- Modify: `skills/shared/references/context-management.md:76-87` (스킬별 토큰 예산 테이블)

- [ ] **Step 1: 토큰 예산 행 추가**

`context-management.md`의 스킬별 토큰 예산 테이블(78-86행)에 plan 행을 추가한다. sermon 행 뒤에:

```
| plan (세션당) | 15K | 20K | 5K | 40K |
```

- [ ] **Step 2: plan 단계 컨텍스트 관리 섹션 추가**

review 단계 컨텍스트 관리(135-139행) 뒤에 새 섹션 추가:

```markdown
## plan 단계 컨텍스트 관리

1. 프로필 로드: style.yaml + theology.yaml = ~2K 토큰 (상시 유지)
2. plan.yaml: ~1K 토큰 (상시 유지)
3. KB 검색: Level 0~1 위주, 한 번에 10K 토큰 이하
4. interview_log.md: 500줄 초과 시 현재 phase만 로드 (이전 phase는 plan.yaml에 구조화)
5. proposal.md: 갱신 시에만 생성/쓰기, 컨텍스트에 상시 유지하지 않음
```

- [ ] **Step 3: 검증**

테이블에 plan 행 존재, plan 단계 컨텍스트 관리 섹션 존재 확인.

- [ ] **Step 4: 커밋**

```bash
git add skills/shared/references/context-management.md
git commit -m "feat: add plan skill token budget to context-management"
```

---

## Chunk 2: publish-plan 스킬 생성

새 스킬의 SKILL.md와 참조 문서를 만든다.

### Task 3: interview-guide.md 참조 문서 생성

**Files:**
- Create: `skills/publish-plan/references/interview-guide.md`

- [ ] **Step 1: 인터뷰 가이드 작성**

스펙 섹션 5(소크라테스 인터뷰 워크플로우)를 실행 가능한 가이드로 작성한다. 포함할 내용:

```markdown
---
name: interview-guide
description: publish-plan 소크라테스 인터뷰 5단계 질문 가이드 + 유형별 깊이 조절 규칙
---

# 소크라테스 인터뷰 가이드

## 진행 규칙

1. 한 번에 한 질문
2. KB 기반 제안 — 초반 KB 현황 제시, 대화 중 자연스럽게 자료 활용
3. 저자의 답변 존중 — 방향을 주도하지 않음, 질문으로 발견 유도
4. 단계 완료 판단 — plan.yaml 필드가 충분히 채워지면 다음 단계 제안
5. 매 단계 완료 시 자동 저장 — plan.yaml + proposal.md + interview_log.md 갱신
6. 중단/재개 — 언제든 현재 상태 저장 가능

## Phase 1: concept (컨셉)

### 목표
왜 이 책을 쓰는가, 이 책이 답하려는 핵심 질문은 무엇인가.

### 산출물
plan.yaml의 concept.motivation, concept.core_question, concept.working_title

### KB 활용
- 사용자가 주제를 언급하면 wiki/ 관련 현황 제시
- "이 주제로 설교 N편, 개념 기사 M개가 KB에 있습니다"

### 질문 예시 (유형별)

**new_book:**
- "어떤 주제로 책을 쓰고 싶으신가요?"
- "이 책을 통해 답하고 싶은 질문이 있나요?"
- "이 주제에 대해 기존에 쓰신 것과 다른 접근이 있나요?"
- "가제가 있으신가요?"

**sermon_collection:**
- "어떤 설교들을 모으고 싶으신가요? 특정 주제? 기간?"
- "이 설교집의 제목이나 방향은?"

**commentary:**
- "어떤 성경 본문을 강해하고 싶으신가요?"
- "이 강해서의 특별한 접근 방식이 있나요?"

**revision:**
- "어떤 책을 개정하려 하시나요?"
- "개정하려는 이유가 무엇인가요?"

### 완료 기준
motivation, core_question, working_title 모두 비어있지 않으면 다음 단계 제안.

---

## Phase 2: audience (독자)

### 목표
누가 이 책을 읽는가, 독자가 무엇을 얻어가는가.

### 산출물
plan.yaml의 audience.primary, audience.prior_knowledge, audience.reader_outcome

### KB 활용
- sermon_pattern.yaml의 청중 관련 정보 참조
- 기존 설교 대상 패턴에서 독자층 추론 제안

### 질문 예시

**new_book (상세):**
- "이 책의 주요 독자는 누구인가요? (평신도/신학생/목회자)"
- "독자가 이 주제에 대해 얼마나 알고 있다고 가정하나요?"
- "이 책을 다 읽은 독자가 무엇을 할 수 있게 되면 좋겠나요?"

**sermon_collection / commentary / revision (간략):**
- "이 책의 주 독자층은 누구인가요?"
- "독자가 얻어갈 핵심은?"

### 완료 기준
primary, reader_outcome이 비어있지 않으면 다음 단계 제안.

---

## Phase 3: message (메시지)

### 목표
이 책의 핵심 주장은 무엇인가.

### 산출물
plan.yaml의 message.thesis, message.key_themes, message.theological_stance

### KB 활용
- theology.yaml에서 저자의 신학적 입장 끌어옴
- wiki/concepts/에서 주제 관련 기사 검색
- "선생님의 KB를 보면 {주제}에 대해 {입장}을 가지고 계신데, 이 책에서도 이 방향인가요?"

### 질문 예시

**new_book / commentary (상세):**
- "이 책에서 가장 강조하고 싶은 메시지는 무엇인가요?"
- "한 문장으로 이 책의 핵심 주장을 말한다면?"
- "다루고 싶은 핵심 주제들을 나열해주세요"
- "신학적으로 특별히 강조하고 싶은 방향이 있나요?"

**sermon_collection (전체 방향):**
- "이 설교 모음을 관통하는 메시지가 있나요?"
- "독자가 이 설교들에서 발견하길 바라는 것은?"

**revision (변경점):**
- "초판 대비 강조점이 바뀐 부분이 있나요?"

### 완료 기준
thesis, key_themes(1개 이상)이 비어있지 않으면 다음 단계 제안.

---

## Phase 4: structure (구조)

### 목표
몇 장으로 구성할 것인가, 어떤 논리 흐름인가.

### 산출물
plan.yaml의 structure.total_chapters, structure.estimated_length, structure.flow_type, outline 초안

### KB 활용
- KB 기사 클러스터 분석으로 목차 후보 제안
- "KB에서 {주제} 관련 기사들을 분석해보면, 이런 흐름이 자연스러울 것 같습니다: ..."
- wiki/concepts/_index.md + wiki/sermons/_index.md 스캔

### 질문 예시

**new_book (상세):**
- "목차 구상이 있으신가요, 아니면 제가 KB를 분석해서 제안해드릴까요?"
- (사용자 목차 제공 시) "이 흐름이 맞는지 확인합니다..."
- (KB 분석 제안 시) "KB를 분석해보니 이런 구조는 어떨까요? [목차 제안]"
- "전체적으로 연역적/귀납적/내러티브 어떤 흐름이 좋을까요?"
- "예상 분량은 어느 정도로 생각하시나요?"

**sermon_collection (배치 중심):**
- "설교를 시간순으로 배치할까요, 주제별로 묶을까요?"
- (시간순) "KB에 {N}편의 설교가 있습니다. 전체를 포함할까요?"
- (주제별) "이런 주제 그룹으로 묶어볼 수 있습니다: [그룹 제안]"

**commentary (본문 단위):**
- "장 단위로 구성할까요, 단락 단위로 구성할까요?"
- "KB에 이 범위의 본문 기사가 {N}개 있습니다"

**revision (변경 방향):**
- "원본의 목차 구조를 유지할까요, 변경할 부분이 있나요?"

### 완료 기준
total_chapters > 0이고 outline에 1개 이상 항목이 있으면 다음 단계 제안.

---

## Phase 5: detail (상세)

### 목표
각 챕터에서 무엇을 말하는가.

### 산출물
plan.yaml outline의 각 항목: core_argument, sections(유형별), kb_sources, estimated_length, notes

### KB 활용
- 챕터별 관련 KB 기사 매칭
- "이 챕터에서 활용할 수 있는 자료가 wiki에 {N}개 있습니다: [기사 목록]"

### 유형별 깊이

**new_book — B 수준 (섹션 구조까지):**
각 챕터마다:
- 핵심 논지 (core_argument)
- 섹션 구성 (sections: 도입-본론1-본론2-결론 등)
- 참조 KB 기사 (kb_sources)
- 예상 분량 (estimated_length)

**sermon_collection — A 수준 (가벼움):**
각 설교마다:
- 핵심 메시지 (core_argument) — 설교 자체의 메시지 보존
- 참조 KB 기사 (kb_sources)
- sections는 비워둠 (설교 원본 구조 보존)

**commentary — 접근 방향 중심:**
각 본문 단위마다:
- 강해 방향 (core_argument)
- 참조 KB 기사 (kb_sources) — passages/ + concepts/ + references/
- 특별히 강조할 원어/신학 포인트 (notes)

**revision — 변경 포인트 중심:**
각 섹션마다:
- 변경/보완 방향 (core_argument)
- 참조 KB 기사 (kb_sources) — 새로 추가된 자료 중심
- 구체적 변경 내용 (notes)

### 완료 기준
outline의 모든 항목에 core_argument가 채워지면 finalize 제안.

---

## 커스텀 인터뷰 가이드

`custom-interview-guide.md` 파일이 같은 디렉토리에 존재하면 이 가이드에 **추가로** 적용한다.
커스텀 가이드에는 특정 사용자/교회에 맞는 질문이나 단계를 정의할 수 있다.
```

- [ ] **Step 2: 검증**

파일 읽어서 확인:
- frontmatter (name, description) 존재
- 5개 phase 모두 포함 (concept, audience, message, structure, detail)
- 유형별 깊이 조절 명시 (new_book, sermon_collection, commentary, revision)
- 커스텀 가이드 패턴 언급

- [ ] **Step 3: 커밋**

```bash
git add skills/publish-plan/references/interview-guide.md
git commit -m "feat: add interview guide reference for publish-plan"
```

### Task 4: publish-plan SKILL.md 생성

**Files:**
- Create: `skills/publish-plan/SKILL.md`

- [ ] **Step 1: SKILL.md 작성**

스펙 섹션 3.1, 5, 6의 내용을 SKILL.md 형식으로 작성한다:

```markdown
---
name: publish-plan
description: Use when users say "/publish-plan", "기획해줘", "책 기획", "기획안 만들어줘", "plan a book", or want to plan a book before writing
---

# Publish Plan — 소크라테스 인터뷰 기반 기획

저자의 KB와 프로필을 기반으로 소크라테스식 인터뷰를 통해 책 기획을 구체화한다. 기획안은 독립 엔티티로 관리되며, 확정 시 project로 변환하여 /publish-write와 연동한다.

## 트리거 조건

- "/publish-plan"
- "/publish-plan new"
- "/publish-plan {plan_id}"
- "/publish-plan list"
- "/publish-plan delete {plan_id}"
- "/publish-plan finalize {plan_id}"
- "기획해줘", "책 기획", "기획안 만들어줘"
- "새 책 구상", "출판 기획"
- "plan a book", "book planning"

## 사전 조건

1. **config.yaml 존재** — 워크스페이스가 초기화된 상태
2. **wiki/ 에 기사 존재** (권장) — KB가 구축된 상태에서 더 풍부한 기획 가능. 없어도 진행은 가능하지만 KB 기반 제안이 제한됨

## WHEN TRIGGERED - EXECUTE IMMEDIATELY

### Step 0: plans/ 디렉토리 확인

config.yaml을 읽어 워크스페이스 경로를 확인한다. `plans/` 디렉토리가 없으면 자동 생성한다.

### Step 1: 동작 모드 결정

트리거 인자를 분석하여 동작 모드를 결정한다:

| 인자 | 동작 |
|------|------|
| (없음) | 기획안 목록 표시 + 새로 만들기/이어하기 선택 |
| `new` | 새 기획안 시작 → Step 2로 |
| `{plan_id}` | 기존 기획안 이어하기 → Step 4로 |
| `list` | 기획안 목록 표시 |
| `delete {plan_id}` | 기획안 삭제 (사용자 확인 후) |
| `finalize {plan_id}` | 기획안 확정 → Step 6으로 |

**기획안 목록 표시:**
plans/ 하위 모든 plan_{id}/ 디렉토리를 스캔, 각 plan.yaml에서 id, type, status, updated를 읽어 테이블로 표시.

### Step 2: 새 기획안 시작

사용자로부터 기본 정보를 수집한다:

1. **기획안 ID** — 짧은 식별자 (예: 은혜론_2026). sanitize: 공백→_, 특수문자 제거
2. **프로젝트 유형** — new_book / revision / sermon_collection / commentary
3. **주제** (자유 형식) — "은혜에 대한 책", "로마서 강해" 등

plan_{id}/ 디렉토리를 생성하고 초기 plan.yaml, proposal.md, interview_log.md를 작성한다.

**초기 plan.yaml:**
workspace-schema.md의 plan.yaml 스키마(4.8) 참조. status: concept, interview.current_phase: concept으로 초기화.

**초기 proposal.md:**
```markdown
# {working_title 또는 주제}

> 기획 진행 중 — 인터뷰가 진행됨에 따라 자동 갱신됩니다.
```

**초기 interview_log.md:**
```markdown
# 인터뷰 기록 — {working_title 또는 주제}
```

### Step 3: 소크라테스 인터뷰 시작

저자 프로필 4파일을 로드한다 (비어 있어도 진행).

**KB 현황 제시:**
사용자가 언급한 주제로 wiki/ 관련 카테고리의 _index.md를 스캔하여 관련 기사 수를 간략히 알려준다:
- "KB에 {주제} 관련 설교 N편, 개념 기사 M개가 있습니다."

**인터뷰 진행:**
interview-guide.md의 현재 phase 질문 가이드를 참조하여 소크라테스식 대화를 진행한다.

인터뷰 진행 규칙:
1. 한 번에 한 질문
2. KB 기반 제안 — 적절한 시점에 KB 자료를 대화에 녹임
3. 저자의 답변 존중 — 방향을 주도하지 않음
4. 유형별 깊이 조절 — interview-guide.md 참조
5. 저자가 단계를 건너뛰거나 돌아가려 하면 유연하게 대응

**KB 검색 전략:**
shared/references/search-strategy.md의 계층적 검색을 따른다:
- Level 0: 카테고리 _index.md (토큰 최소)
- Level 1: 후보 기사 summary (토큰 소)
- Level 2: 필요 시만 chunks/ (토큰 관리)

**단계 전환:**
interview-guide.md의 각 phase 완료 기준 충족 시 다음 phase를 제안한다. 강제 아님.

phase 전환 시:
1. plan.yaml의 해당 phase 필드에 인터뷰 결과 기록
2. interview.current_phase 갱신, completed_phases에 추가
3. status를 새 phase로 갱신
4. proposal.md 해당 섹션 갱신
5. interview_log.md에 대화 기록 추가

### Step 4: 기존 기획안 재개

1. plans/plan_{plan_id}/plan.yaml 로드
2. interview.current_phase, completed_phases, next_question_context 확인
3. interview_log.md에서 현재 phase의 대화 기록 로드 (500줄 초과 시 현재 phase만)
4. 저자 프로필 4파일 로드
5. "지난번에 {phase} 단계까지 진행했습니다. {next_question_context} 이어서 진행할까요?"
6. Step 3의 인터뷰로 진행

### Step 5: 중단 및 저장

사용자가 중단을 요청하거나 세션이 종료될 때:

1. 현재까지의 인터뷰 결과를 plan.yaml에 저장
2. interview.next_question_context에 "다음에 이어갈 맥락" 요약 기록
3. proposal.md를 현재까지의 기획 상태로 갱신
4. interview_log.md에 현재 세션 대화 기록 추가
5. "기획안 '{id}'를 저장했습니다. 다음에 /publish-plan {id}로 이어서 작업할 수 있습니다."

### Step 6: 기획안 확정 (finalize)

모든 phase가 완료되었거나, 사용자가 현재 상태로 확정을 원할 때:

**사전 확인:**
- outline에 최소 1개 이상의 챕터가 있는지 확인
- 비어있는 핵심 필드가 있으면 사용자에게 알림 (강제 아님)

**확정 절차:**

1. 사용자에게 project_name 확인 (기본값: plan_id)
2. plan.yaml의 status를 finalized로 변경, finalized.project_name/finalized_date 기록
3. proposal.md를 최종 상태로 갱신

4. projects/{project_name}/ 디렉토리 생성:
   ```
   projects/{project_name}/
   ├── project.yaml
   ├── proposal.md     ← plans/에서 복사
   ├── drafts/
   ├── reviews/
   └── exports/
   ```

5. project.yaml 생성 — plan.yaml → project.yaml 변환:
   - name ← title
   - type ← type
   - author_id ← author_id
   - created ← 오늘 날짜
   - status ← drafting
   - plan_id ← id
   - summary ← concept + audience + message 요약
   - flow_type ← structure.flow_type
   - outline ← plan의 outline (각 항목에 slug, draft_file 자동 생성)
   - base_document ← (revision인 경우 사용자에게 확인)
   - wiki_queries ← message.key_themes

6. 완료 리포트:
   ```
   기획안 '{id}' 확정 완료

   프로젝트: {project_name}
   유형: {type}
   챕터: {N}개
   저장 위치: projects/{project_name}/

   다음 단계:
   /publish-write를 실행하면 이 기획안을 기반으로 집필을 시작합니다.
   ```

원본 plans/plan_{id}/는 아카이브로 보존한다 (삭제하지 않음).

---

## 참조 문서

- `shared/references/workspace-schema.md` — plans/ 구조 + plan.yaml 스키마
- `shared/references/search-strategy.md` — wiki/ 계층적 검색 전략
- `shared/references/author-profile-schema.md` — 저자 프로필 4파일 스키마
- `shared/references/context-management.md` — plan 스킬 토큰 예산
- `publish-plan/references/interview-guide.md` — 5단계 인터뷰 질문 가이드
- `publish-plan/references/custom-interview-guide.md` — 사용자별 커스텀 (있으면 추가 적용)
```

- [ ] **Step 2: 검증**

파일을 읽어서 확인:
- frontmatter (name, description) 존재
- 트리거 조건 한/영 포함
- "WHEN TRIGGERED - EXECUTE IMMEDIATELY" 패턴
- CRUD 전체 흐름 (list, new, resume, delete, finalize)
- 소크라테스 인터뷰 규칙 포함
- finalize → project 변환 로직
- 참조 문서 경로 정확

- [ ] **Step 3: 커밋**

```bash
git add skills/publish-plan/
git commit -m "feat: add publish-plan skill with Socratic interview workflow"
```

---

## Chunk 3: 기존 스킬 수정

### Task 5: publish-setup SKILL.md에 plans/ 추가

**Files:**
- Modify: `skills/publish-setup/SKILL.md:111-128` (Step 3 디렉토리 구조)

- [ ] **Step 1: 디렉토리 구조에 plans/ 추가**

`skills/publish-setup/SKILL.md`의 Step 3 디렉토리 트리(113-128행)에서 `projects/` 앞에 `plans/`를 추가:

```
├── plans/
```

- [ ] **Step 2: 검증**

트리에 plans/ 포함 확인.

- [ ] **Step 3: 커밋**

```bash
git add skills/publish-setup/SKILL.md
git commit -m "feat: add plans/ directory to publish-setup workspace structure"
```

### Task 6: publish-write SKILL.md 수정

**Files:**
- Modify: `skills/publish-write/SKILL.md` (Step 1~2 제거, project 선택 시작으로 변경)

- [ ] **Step 1: Step 1 교체 — 프로젝트 선택으로 변경**

기존 Step 1(41-58행, "프로젝트 유형 및 목차 확인")을 완전히 교체:

```markdown
### Step 1: 프로젝트 선택

config.yaml을 로드하여 워크스페이스 경로를 확인한 뒤, `projects/` 디렉토리를 스캔한다.

**프로젝트가 있는 경우:**
- 프로젝트 목록을 표시 (project.yaml의 name, type, status 읽기)
- 사용자가 선택하거나, 이미 대화에서 특정 프로젝트를 언급한 경우 해당 프로젝트 선택

**프로젝트가 없는 경우:**
- "/publish-plan을 먼저 실행하여 기획을 완성한 후 집필을 시작하세요." 안내
- 스킬 종료

**선택된 프로젝트 로드:**
1. project.yaml 로드 — outline, type, wiki_queries 확인
2. proposal.md 로드 (있으면, ~1-2K 토큰) — 기획 의도·독자·메시지 맥락 참조
3. proposal.md는 집필 시 전체 방향을 상기하는 용도. 챕터 작업 중 토큰 부족 시 요약만 유지
```

- [ ] **Step 2: Step 2 교체 — 프로필 로드로 변경**

기존 Step 2(60-94행, "프로젝트 초기화")를 제거하고, 기존 Step 3(96-107행, "저자 프로필 로드")의 내용을 Step 2로 번호 변경.

- [ ] **Step 3: 이후 Step 번호 재조정**

기존 Step 3 → Step 2 (저자 프로필 로드)
기존 Step 4 → Step 3 (챕터별 초안 작성)
기존 Step 5 → Step 4 (자기 검증)
기존 Step 6 → Step 5 (개정판 모드)
기존 Step 7 → Step 6 (초안 저장 및 완료 리포트)

- [ ] **Step 4: 사전 조건 수정**

사전 조건(28-36행)의 3번 항목을 변경:

기존:
```
3. **wiki/ 에 기사 존재** — wiki/_index.md에 기사가 1개 이상 등록된 상태
```

변경:
```
3. **프로젝트 존재** — projects/ 에 확정된 프로젝트가 1개 이상 존재 (/publish-plan finalize 완료)
```

- [ ] **Step 5: 참조 문서에 proposal.md 추가**

참조 문서 목록(269-277행)에 추가:
```
- proposal.md (프로젝트 디렉토리 내) — 기획 의도·독자·메시지 맥락 (집필 방향 참조용)
```

- [ ] **Step 6: 검증**

파일을 읽어서 확인:
- Step 1이 프로젝트 선택으로 시작
- 프로젝트 초기화 로직 없음
- proposal.md 로드 로직 포함
- Step 번호 연속성

- [ ] **Step 7: 커밋**

```bash
git add skills/publish-write/SKILL.md
git commit -m "refactor: publish-write starts from project selection, removes planning logic"
```

### Task 7: writing-modes.md에서 목차 로직 제거

**Files:**
- Modify: `skills/publish-write/references/writing-modes.md:63-82` (new_book 1단계: 목차 확정)

- [ ] **Step 1: new_book 1단계 교체**

기존 "1단계: 목차 확정"(73-82행)의 "목차가 없는 경우 (KB 기반 자동 제안)" 부분을 제거하고, 다음으로 교체:

```markdown
#### 1단계: 프로젝트 확인

project.yaml의 outline을 확인한다. `/publish-plan`에서 이미 목차가 확정된 상태이므로:
- outline의 각 챕터 제목과 core_argument 확인
- proposal.md에서 기획 의도, 독자, 핵심 메시지 확인
- wiki_queries에서 참조 토픽 확인
```

- [ ] **Step 2: 검증**

"KB 기반 자동 제안" 로직이 제거되었는지 확인.

- [ ] **Step 3: 커밋**

```bash
git add skills/publish-write/references/writing-modes.md
git commit -m "refactor: remove TOC generation logic from writing-modes, now handled by publish-plan"
```

---

## Chunk 4: 프로젝트 문서 갱신

### Task 8: CLAUDE.md 스킬 목록 갱신

**Files:**
- Modify: `CLAUDE.md` (스킬 목록 테이블)

- [ ] **Step 1: 스킬 목록에 publish-plan 추가**

CLAUDE.md의 스킬 목록 테이블에서 `/publish-profile`과 `/publish-write` 사이에 추가:

```
| `/publish-plan` | 소크라테스 인터뷰 기반 기획 (컨셉·독자·메시지·구조·상세) |
```

- [ ] **Step 2: 사용법 섹션 갱신**

"일상 사용" 섹션의 예시를 갱신:
기존: `"새 책 써줘" → write → review → export`
변경: `"새 책 기획해줘" → plan → write → review → export`

- [ ] **Step 3: 커밋**

```bash
git add CLAUDE.md
git commit -m "docs: add publish-plan to skill list in CLAUDE.md"
```

### Task 9: 원본 설계 문서 갱신

**Files:**
- Modify: `docs/specs/2026-04-21-publish-agent-design.md` (스킬 테이블 + 파이프라인)

- [ ] **Step 1: 스킬 테이블에 publish-plan 추가**

섹션 2의 스킬 테이블(56-66행)에서 `/publish-profile`(#3)과 `/publish-write`(#4) 사이에 추가하고 이후 번호 재조정:

```
| 4 | `/publish-plan` | 소크라테스 인터뷰 기반 기획 | KB 읽기 |
```

기존 #4~8 → #5~9로 재번호. "총 9개 스킬"(54행)을 "총 10개 스킬"로 변경.

- [ ] **Step 2: 파이프라인 다이어그램 갱신**

섹션 1.2의 다이어그램(28-44행)에서 `/publish-profile` 뒤에 `/publish-plan`을 삽입:

```
/publish-profile  → authors/ (저자 프로필)
                        ↓
/publish-plan     → plans/ (기획안)
                        ↓
              ┌─────────┼─────────┐
              ↓         ↓         ↓
      /publish-write  /publish-sermon  /publish-curate
```

- [ ] **Step 3: 검증**

스킬 수 10개, 파이프라인에 publish-plan 포함 확인.

- [ ] **Step 4: 커밋**

```bash
git add docs/specs/2026-04-21-publish-agent-design.md
git commit -m "docs: add publish-plan to design spec skill table and pipeline diagram"
```

---

## Task Dependencies

```
Task 1 (workspace-schema) ─┐
Task 2 (context-mgmt)     ─┼→ Task 3 (interview-guide) → Task 4 (SKILL.md)
                            │
Task 5 (setup) ─────────────┘
Task 6 (write) ──────── (독립)
Task 7 (writing-modes) ─ (Task 6 이후)
Task 8 (CLAUDE.md) ───── (독립)
Task 9 (design spec) ─── (독립)
```

Task 1-2는 공유 참조 수정이므로 먼저 완료. Task 3-4는 순차. Task 5-9는 병렬 가능.

## Execution Notes

- 이 프로젝트는 코드가 아닌 **스킬 파일(마크다운)** 작성이므로, TDD 대신 "스펙 대비 검증" 패턴을 사용한다
- 각 스킬 작성 후 검증: frontmatter 존재, 트리거 조건 포함, 워크플로우가 스펙과 일치, 참조 문서 경로 정확
- 스킬 간 참조 경로는 상대 경로 (`shared/references/...`) 사용
