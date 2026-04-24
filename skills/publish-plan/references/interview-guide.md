---
name: interview-guide
description: publish-plan 소크라테스 인터뷰 5단계 질문 가이드 + 유형별 깊이 조절 규칙
---

# 소크라테스 인터뷰 가이드

## 진행 규칙

1. **한 번에 한 질문** — 여러 질문을 한꺼번에 던지지 않음
2. **KB 기반 제안** — 초반 KB 현황 제시, 대화 중 자연스럽게 자료 활용
3. **저자의 답변 존중** — 방향을 주도하지 않음, 질문으로 발견 유도
4. **단계 완료 판단** — plan.yaml 필드가 충분히 채워지면 다음 단계 제안 (강제 아님)
5. **매 단계 완료 시 자동 저장** — plan.yaml + proposal.md + interview_log.md 갱신
6. **중단/재개** — 언제든 현재 상태 저장 가능

---

## Phase 1: concept (컨셉)

### 목표

왜 이 책을 쓰는가, 이 책이 답하려는 핵심 질문은 무엇인가.

### 산출물

plan.yaml의 `concept.motivation`, `concept.core_question`, `concept.working_title`

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

plan.yaml의 `audience.primary`, `audience.prior_knowledge`, `audience.reader_outcome`

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

plan.yaml의 `message.thesis`, `message.key_themes`, `message.theological_stance`

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

plan.yaml의 `structure.total_chapters`, `structure.estimated_length`, `structure.flow_type`, `outline` 초안

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

plan.yaml outline의 각 항목: `core_argument`, `sections`(유형별), `kb_sources`, `estimated_length`, `notes`

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
