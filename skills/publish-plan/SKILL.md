---
name: publish-plan
description: Use when users say "/publish-plan", "기획해줘", "책 기획", "기획안 만들어줘", "기획 이어하자", "기획 목록", "plan a book", "book planning", "기획 확정", "finalize plan", or want to plan, design, or outline a book before writing
---

# Publish Plan — 소크라테스 인터뷰 기반 기획

저자와 소크라테스식 인터뷰를 통해 책의 컨셉, 독자, 메시지, 구조, 상세 목차를 단계적으로 구체화한다. KB(위키)를 인터뷰 과정에 자연스럽게 활용하며, 기획안을 독립 엔티티로 CRUD 관리한다. 기획 확정 시 project로 변환하여 `/publish-write`와 연동한다.

## 트리거 조건

```
- "/publish-plan"                     → 기획안 목록 + 새로 만들기/이어하기 선택
- "/publish-plan new"                 → 새 기획안 시작
- "/publish-plan {plan_id}"           → 기존 기획안 이어하기
- "/publish-plan list"                → 기획안 목록 + 상태 요약
- "/publish-plan delete {plan_id}"    → 기획안 삭제 (확인 후)
- "/publish-plan finalize {plan_id}"  → 기획안 확정 → project로 변환
- "기획해줘"
- "책 기획"
- "기획안 만들어줘"
- "기획 이어하자"
- "기획 목록"
- "기획 확정해줘"
- "plan a book"
- "book planning"
- "finalize plan"
```

## 사전 조건

1. **config.yaml 존재** — 워크스페이스가 초기화된 상태 (`/publish-setup` 완료)
2. **wiki/ 권장** — KB가 있으면 인터뷰 중 자료를 활용. 없어도 기획 자체는 진행 가능

사전 조건 미충족 시: config.yaml이 없으면 `/publish-setup`을 먼저 실행하도록 안내한다.

---

## WHEN TRIGGERED - EXECUTE IMMEDIATELY

### Step 0: plans/ 디렉토리 확인

워크스페이스 루트에 `plans/` 디렉토리가 있는지 확인한다. 없으면 자동 생성한다.

```
{workspace}/plans/    ← 없으면 자동 생성
```

기존 워크스페이스 사용자가 `/publish-setup`을 다시 실행할 필요 없도록 이 스킬이 자체적으로 보장한다.

### Step 1: 동작 모드 결정

트리거 인자에 따라 분기한다:

| 인자 | 동작 |
|------|------|
| (없음) | `plans/` 스캔 → 기획안 목록 표시 + "새로 만들기" / "ID 입력하여 이어하기" 제안 |
| `new` | → **Step 2** (새 기획안 생성) |
| `{plan_id}` | → **Step 4** (기존 기획안 재개) |
| `list` | `plans/` 스캔 → 기획안 목록 + 상태 요약 표시 후 종료 |
| `delete {plan_id}` | 해당 기획안 삭제 확인 → 확인 시 `plans/plan_{id}/` 디렉토리 삭제 후 종료 |
| `finalize {plan_id}` | → **Step 6** (기획안 확정 → project 변환) |

**기획안 목록 표시 형식:**

```
기획안 목록

ID               유형               상태           마지막 작업
--------------------------------------------------------------
은혜론_2026      new_book          detail         2026-04-24
로마서강해       commentary        audience       2026-04-23
설교모음_1       sermon_collection finalized      2026-04-20

[new] 새 기획안 시작  |  기획안 ID를 입력하면 이어서 작업합니다
```

인자 없이 트리거된 경우, 목록을 보여준 뒤 사용자 선택을 기다린다.

### Step 2: 새 기획안 생성

사용자로부터 다음 정보를 수집한다. 이미 대화에서 언급된 경우 재질문 없이 진행한다.

**필수:**
- **plan_id**: 짧은 식별자 (예: `은혜론_2026`, `로마서강해`)
- **type**: `new_book` / `revision` / `sermon_collection` / `commentary`
- **topic**: 기획할 책의 주제 (간단한 설명)

**plan_id sanitize 규칙:**
- 공백 → `_`
- 특수문자 제거
- 한글, 영문, 숫자, 언더스코어(`_`)만 허용

수집 완료 후 다음 파일들을 생성한다:

**디렉토리:** `plans/plan_{id}/`

**plan.yaml:**

```yaml
id: "{plan_id}"
title: ""
type: {type}
author_id: "{config.yaml의 author.id}"
created: {오늘 날짜 YYYY-MM-DD}
updated: {오늘 날짜 YYYY-MM-DD}
status: concept

interview:
  current_phase: concept
  completed_phases: []
  next_question_context: ""

concept:
  motivation: ""
  core_question: ""
  working_title: ""

audience:
  primary: ""
  prior_knowledge: ""
  reader_outcome: ""

message:
  thesis: ""
  key_themes: []
  theological_stance: ""

structure:
  total_chapters: 0
  estimated_length: ""
  flow_type: ""

outline: []

finalized:
  project_name: ""
  finalized_date: ""
```

**proposal.md:**

```markdown
# (가제 미정)

> 기획 진행 중 — concept 단계

## 기획 의도
(인터뷰 진행 후 작성)

## 대상 독자
(인터뷰 진행 후 작성)

## 핵심 메시지
(인터뷰 진행 후 작성)

## 목차 구성
(인터뷰 진행 후 작성)
```

**interview_log.md:**

```markdown
# 인터뷰 기록 - {topic}

## Phase: concept ({오늘 날짜})

```

파일 생성 후 즉시 **Step 3**으로 진행한다.

### Step 3: 소크라테스 인터뷰

#### 3a: 저자 프로필 로드

`authors/{author_id}/` 아래 프로필 4파일을 로드한다 (~2K 토큰, 세션 전체에서 유지):

```
authors/{author_id}/style.yaml
authors/{author_id}/theology.yaml
authors/{author_id}/sermon_pattern.yaml
authors/{author_id}/vocabulary.md
```

프로필이 없으면 프로필 없이 진행 가능. 단, KB 기반 제안의 품질이 떨어질 수 있음을 안내한다.

#### 3b: KB 현황 스캔 (wiki/ 존재 시)

사용자가 언급한 주제로 wiki/ 현황을 간략히 파악한다:

```
Level 0: wiki/{관련 카테고리}/_index.md 스캔
→ "이 주제로 설교 N편, 개념 기사 M개가 KB에 있습니다"
```

KB 검색은 `shared/references/search-strategy.md`의 계층적 검색을 따른다. 한 번에 10K 토큰을 초과하지 않는다.

#### 3c: 인터뷰 진행

`publish-plan/references/interview-guide.md`에 따라 5단계 인터뷰를 진행한다.

**커스텀 가이드:** `publish-plan/references/custom-interview-guide.md`가 존재하면 기본 가이드에 추가로 적용한다.

**인터뷰 5단계:**

```
concept → audience → message → structure → detail
```

각 단계는 순서가 있지만, 저자가 원하면 자유롭게 이동 가능하다. "목차부터 생각해봤어"라면 structure로 점프하고 나중에 concept을 채울 수 있다.

**인터뷰 진행 규칙:**

1. **한 번에 한 질문** — 여러 질문을 한꺼번에 던지지 않음
2. **KB 기반 제안** — 초반에 KB 현황을 간략히 보여주고, 대화 중 적절한 시점에 "KB를 보니 ~인데, 이런 방향은 어떠세요?" 식으로 자료를 자연스럽게 녹임
3. **저자의 답변 존중** — LLM이 방향을 주도하지 않음. 질문으로 저자가 스스로 발견하도록 유도
4. **단계 완료 판단** — 해당 phase의 plan.yaml 필드가 충분히 채워지면 다음 단계 제안 (강제 아님)
5. **매 단계 완료 시 자동 저장** — plan.yaml + proposal.md + interview_log.md 갱신
6. **중단/재개** — 언제든 "여기까지 하자" → **Step 5**로 이동하여 현재 상태 저장

**KB 활용 3시점:**

| 시점 | 설명 | KB 소스 |
|------|------|---------|
| 인터뷰 시작 (concept) | 주제 언급 시 관련 KB 현황 간략 제시 | wiki/_index.md, 카테고리별 _index.md |
| 대화 중 적절한 시점 | 답변에서 키워드 추출 → 관련 KB 기사 검색 → 과거 저술과 일관성 유지 도움 | wiki/concepts/, theology.yaml |
| structure/detail 단계 | KB 기사 클러스터 분석으로 목차 후보 제안, 챕터별 기사 매칭 | wiki/ 전체 카테고리 |

**유형별 인터뷰 깊이 조절:**

| Phase | new_book | sermon_collection | commentary | revision |
|-------|----------|-------------------|------------|----------|
| concept | 깊이 파고듦 | 가벼움 | 범위 확정 중심 | "왜 개정?" 중심 |
| audience | 상세 | 간략 | 간략 | 기존/새 독자 |
| message | 상세 | 전체 방향 | 접근+신학 강조 | 변경 강조점 |
| structure | 상세 | 배치 순서/흐름 | 본문 단위 결정 | 원본 대비 변경 |
| detail | B수준(섹션까지) | A수준(가벼움) | 접근 방향 중심 | 변경 포인트 중심 |

단계별 질문 예시와 완료 기준은 `publish-plan/references/interview-guide.md` 참조.

#### 3d: 단계 전환 (phase transition)

각 단계 완료 시:

1. plan.yaml의 해당 phase 필드 갱신
2. `interview.completed_phases`에 현재 phase 추가
3. `interview.current_phase`를 다음 phase로 변경
4. `status`를 `interview.current_phase`와 동기화

```
current_phase: concept    → status: concept
current_phase: audience   → status: audience
current_phase: message    → status: message
current_phase: structure  → status: structure
current_phase: detail     → status: detail
```

5. proposal.md 해당 섹션 갱신
6. interview_log.md에 새 phase 헤더 추가
7. `plan.yaml`의 `updated` 날짜 갱신

#### 3e: 자동 저장

매 단계 완료 시, 그리고 의미 있는 답변을 받을 때마다 다음 3파일을 갱신한다:

- **plan.yaml** — 구조화된 데이터 (status, phase, 각 섹션 필드)
- **proposal.md** — 사람이 읽기 좋은 기획서 형태
- **interview_log.md** — Q&A 누적 기록

**proposal.md 갱신 형식:**

```markdown
# {title 또는 working_title}

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

**interview_log.md 갱신 형식:**

```markdown
## Phase: {phase} ({날짜})

**Q:** {질문}
**A:** {저자 답변}

**Q:** {질문}
**A:** {저자 답변}

---
```

### Step 4: 기존 기획안 재개

1. `plans/plan_{id}/plan.yaml` 로드 (~1K 토큰, 상시 유지)
2. `interview.current_phase`, `completed_phases`, `next_question_context` 확인
3. `plans/plan_{id}/interview_log.md` 로드
   - 500줄 이하: 전체 로드
   - 500줄 초과: 현재 phase의 대화만 로드 (이전 phase는 plan.yaml에 구조화되어 있으므로 별도 로드 불필요)
4. `plans/plan_{id}/proposal.md` 로드 (현재까지의 기획 상태 파악)
5. 사용자에게 안내:

```
지난번에 {current_phase} 단계까지 진행했습니다.
{next_question_context}
이어서 진행할까요?
```

6. **Step 3a**부터 재개 (프로필 로드 → 인터뷰 계속)

### Step 5: 저장 및 일시 중단

사용자가 "여기까지 하자", "저장해줘", "나중에 이어하자" 등을 요청하면:

1. 현재까지의 인터뷰 내용을 plan.yaml에 반영
2. `interview.next_question_context`에 재개 시 LLM이 참조할 맥락 요약 기록
   - 예: "concept 단계 완료, audience 단계에서 독자층 논의 중. 마지막으로 평신도 대상 여부를 물어볼 차례"
3. plan.yaml의 `updated` 날짜 갱신
4. proposal.md 현재 상태로 갱신
5. interview_log.md에 현재까지의 대화 기록 저장
6. 안내:

```
기획안이 저장되었습니다.

기획안: {id}
상태: {status} ({current_phase} 단계)
저장 위치: plans/plan_{id}/

이어서 작업하려면: /publish-plan {id}
```

### Step 6: 기획안 확정 (finalize)

기획안을 확정하여 project로 변환한다.

#### 6a: 확정 전 검증

1. plan.yaml 로드
2. status가 `detail`이고 outline의 모든 항목에 `core_argument`가 채워져 있는지 확인
3. 미완성 항목이 있으면 안내하고 인터뷰 계속 여부를 묻는다
4. 확정 가능하면 사용자에게 project_name을 확인받는다 (기본값: plan_id)

#### 6b: project 디렉토리 생성

```
projects/{project_name}/
├── project.yaml
├── proposal.md     ← plans/plan_{id}/proposal.md 복사
├── drafts/
├── reviews/
└── exports/
```

#### 6c: project.yaml 생성

plan.yaml에서 project.yaml로 변환한다:

**변환 매핑:**

| plan.yaml | project.yaml |
|-----------|-------------|
| id | plan_id (참조용) |
| title | name |
| type | type |
| author_id | author_id |
| concept + audience + message | summary (요약 필드) |
| structure.flow_type | flow_type |
| outline | outline (slug, draft_file 자동 생성) |
| finalized.project_name | (디렉토리명) |

**project.yaml 스키마:**

```yaml
name: "{title}"
type: {type}
author_id: "{author_id}"
created: {오늘 날짜 YYYY-MM-DD}
status: drafting

plan_id: "{plan_id}"
summary:
  motivation: "{concept.motivation}"
  core_question: "{concept.core_question}"
  audience: "{audience.primary} — {audience.reader_outcome}"
  thesis: "{message.thesis}"
  key_themes: [{message.key_themes}]
flow_type: "{structure.flow_type}"

outline:
  - title: "{챕터 제목}"
    slug: "{ch번호(2자리 0패딩)_{제목 sanitized}}"
    draft_file: "{slug}.md"
    status: pending
    core_argument: "{core_argument}"
    kb_sources: [{kb_sources}]
  # 챕터별로 반복

base_document: ""
wiki_queries:
  - "{message.key_themes에서 추출}"
```

**slug 생성 규칙:**
- `ch{번호(2자리 0패딩)}_{제목 sanitized}` (예: "1장: 은혜의 본질" → `ch01_은혜의_본질`)
- sanitize: 공백 → `_`, 특수문자 제거, 한글/영문/숫자/언더스코어만 허용

#### 6d: plan.yaml 상태 갱신

1. `status: finalized`
2. `finalized.project_name: "{project_name}"`
3. `finalized.finalized_date: "{오늘 날짜}"`
4. 원본 `plans/plan_{id}/`는 아카이브로 보존

#### 6e: 완료 안내

```
기획안이 확정되어 프로젝트로 변환되었습니다.

기획안: plans/plan_{id}/ (아카이브)
프로젝트: projects/{project_name}/
챕터: {N}개
유형: {type}

다음 단계:
집필을 시작하려면 /publish-write를 실행하세요.
```

---

## 컨텍스트 관리

소크라테스 인터뷰는 대화 중심이므로 KB 로드를 최소화한다.

| 항목 | 토큰 예산 | 유지 정책 |
|------|----------|----------|
| 저자 프로필 4파일 | ~2K | 상시 유지 |
| plan.yaml | ~1K | 상시 유지 |
| KB 검색 결과 | 10K 이하 | Level 0~1 위주, 필요 시만 Level 2 |
| interview_log.md | 가변 | 500줄 이하: 전체 / 500줄 초과: 현재 phase만 |
| proposal.md | ~1-2K | 재개 시 로드, 인터뷰 중 필요 시 참조 |

> 상세 규칙: `shared/references/context-management.md` 참조

---

## 커스텀 인터뷰 가이드

`publish-plan/references/custom-interview-guide.md` 파일이 존재하면 기본 interview-guide.md에 **추가로** 적용한다.
커스텀 가이드에는 특정 사용자/교회에 맞는 인터뷰 질문이나 단계를 정의할 수 있다.

## 참조 문서

- `publish-plan/references/interview-guide.md` — 소크라테스 인터뷰 5단계 질문 가이드 + 유형별 깊이 조절 규칙
- `publish-plan/references/custom-interview-guide.md` — 사용자별 인터뷰 커스터마이징 (있으면 추가 적용)
- `shared/references/search-strategy.md` — wiki/ 계층적 요약 검색 전략
- `shared/references/workspace-schema.md` — plan.yaml, project.yaml 스키마 + 워크스페이스 구조
- `shared/references/author-profile-schema.md` — 저자 프로필 4파일 스키마
- `shared/references/context-management.md` — 컨텍스트 윈도우 관리 전략 + 토큰 예산
