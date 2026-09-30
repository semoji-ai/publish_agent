---
name: publish-write
description: Use when users say "/publish-write", "책 써줘", "초안 작성해줘", "3장 초안", "개정판 수정해줘", "설교집 정리해줘", "강해서 써줘", or want to draft or revise a book, sermon collection, or commentary
---

# Publish Write — KB 기반 집필

저자 프로필과 개인 신학 위키(KB)를 기반으로 신규 도서, 개정판, 설교집, 강해서를 집필한다. 모든 초안은 저자의 문체·신학관·설교 구조를 일관되게 반영한다.

## 트리거 조건

```
- "/publish-write"
- "/publish-write [프로젝트명]"
- "책 써줘"
- "초안 작성해줘"
- "3장 초안 써줘"
- "개정판 수정해줘"
- "설교집 정리해줘"
- "강해서 써줘"
- "새 책 시작하자"
- "원고 작업 시작"
- "chapter draft", "write chapter"
- "revision mode", "revise book"
```

## 사전 조건

다음 세 가지가 모두 충족되어야 한다:

1. **config.yaml 존재** — 워크스페이스가 초기화된 상태 (`/publish-setup` 완료)
2. **저자 프로필 존재** — `authors/{author_id}/` 아래 4개 파일에 내용이 채워진 상태 (`/publish-profile` 완료)
3. **프로젝트 존재** — `projects/` 에 확정된 프로젝트가 1개 이상 존재 (`/publish-plan` finalize 완료)

사전 조건 미충족 시: 어느 단계가 누락되었는지 안내하고 해당 스킬을 먼저 실행하도록 안내한다.

---

## 실행 절차

### Step 1: 프로젝트 선택

config.yaml을 로드하여 워크스페이스 경로를 확인한 뒤, `projects/` 디렉토리를 스캔한다.

**프로젝트가 있는 경우:**
- 프로젝트 목록을 표시 (project.yaml의 name, type, status 읽기)
- 사용자가 선택하거나, 이미 대화에서 특정 프로젝트를 언급한 경우 해당 프로젝트 선택

**프로젝트가 없는 경우:**
- "/publish-plan을 먼저 실행하여 기획을 완성한 후 집필을 시작하세요." 안내
- 스킬 종료

**선택된 프로젝트 로드:**
1. project.yaml 로드 — outline, type, wiki_queries, summary, flow_type 확인
2. proposal.md 로드 (있으면, ~1-2K 토큰) — 기획 의도·독자·메시지 맥락 참조
3. proposal.md는 집필 시 전체 방향을 상기하는 용도. 챕터 작업 중 토큰 부족 시 요약만 유지

### Step 2: 저자 프로필 로드

집필 전 저자 프로필 4개 파일을 모두 로드한다. 이 프로필이 집필 전 과정에서 문체·관점의 기준이 된다.

```
authors/{author_id}/style.yaml          — 어투, 문장 구조, 수사법
authors/{author_id}/theology.yaml       — 신학적 입장 (구원론, 종말론 등)
authors/{author_id}/sermon_pattern.yaml — 설교 구조 패턴 (sermon_collection/commentary용)
authors/{author_id}/vocabulary.md       — 자주 쓰는/피하는 표현
```

프로필 4파일은 합산 ~2K 토큰으로, 세션 전체에서 컨텍스트에 항상 유지한다. 챕터 교체 시에도 프로필은 제거하지 않는다.

### Step 3: 챕터별 초안 작성

**컨텍스트 관리 원칙 (필수):**
- **한 번에 1챕터만 작업한다.** 이전 챕터의 전체 원문은 파일로 저장한 뒤 컨텍스트에서 제거한다. 이전 챕터 요약(5-10줄)만 유지하여 연결성을 보장한다.
- **wiki/ 검색은 계층적으로** — Level 0(_index.md) → Level 1(summary) → Level 2(chunks) 순서로 진입하며, 충분한 정보를 확보하면 더 깊이 들어가지 않는다. 전체 기사를 한 번에 로드하지 않는다.
- **관련 기사는 3-5개 상한** — 한 챕터 작업 시 로드하는 wiki 기사는 최대 5개. 20K 토큰 초과 방지.
- **챕터 완료 후 즉시 파일 저장** — 초안 완성 즉시 `drafts/`에 저장하고 컨텍스트에서 원문 제거. 챕터 요약만 남긴다.
- 토큰 예산: 챕터당 읽기 40K + 처리 40K + 출력 30K = 110K. 나머지는 프로필 + 대화 이력에 할당.

→ 상세 규칙: `shared/references/context-management.md`의 "write 단계 컨텍스트 관리" 섹션 참조

각 챕터에 대해 다음 순서로 진행한다:

#### 3a: wiki/ 계층 검색

`shared/references/search-strategy.md`의 검색 전략을 따른다:

```
Level 0: wiki/{관련 카테고리}/_index.md 스캔
         → 챕터 주제와 관련된 기사 후보 선정
         ↓ (관련 기사 발견 시)
Level 1: 후보 기사의 index.md summary 필드 확인
         → 관련성 판단, 필요한 기사 선별
         ↓ (상세 내용 필요 시)
Level 2: 선별된 기사의 chunks/ 로드
         → 집필에 활용할 실제 내용 확보
```

**검색 카테고리 우선순위:**

| 프로젝트 유형 | 주 검색 카테고리 | 보조 검색 카테고리 |
|--------------|----------------|------------------|
| new_book | concepts/ | sermons/, books/, references/ |
| revision | (원본 기반) | concepts/, books/ |
| sermon_collection | sermons/ | concepts/, passages/ |
| commentary | passages/ | concepts/, references/ |

#### 3b: 관련 자료 로드

검색으로 선별된 자료를 로드한다. 토큰 예산을 고려하여 **가장 관련성 높은 기사 3-5개**를 우선 로드한다. Level 1(summary)에서 충분하면 Level 2(chunks) 로드 금지. 전체 wiki 기사 로드 총량은 20K 토큰을 초과하지 않는다.

#### 3c: 프로필 기반 초안 작성

로드한 KB 자료와 저자 프로필을 바탕으로 챕터 초안을 작성한다.

집필 시 준수 사항:
- **어투:** style.yaml의 `tone` 필드 기준 (경어체/평어체 등)
- **문장 길이:** style.yaml의 `sentence_length` 범위 내
- **수사법:** style.yaml의 `rhetoric` 패턴 활용 (은유, 대조 등)
- **신학적 관점:** theology.yaml의 저자 입장과 일관되게
- **어휘:** vocabulary.md의 자주 쓰는 표현 적극 활용, 피하는 표현 배제
- **설교/강해 구조:** sermon_pattern.yaml 참조 (sermon_collection, commentary)

**개정판 모드(revision):** Step 5 참조.

### Step 4: 자기 검증

각 챕터 초안 완료 후, 다음 체크리스트로 저자 프로필 대비 일관성을 검증한다.

```
[ ] 어투가 style.yaml과 일치하는가?
[ ] 문장 길이가 style.yaml 범위 내인가?
[ ] vocabulary.md의 피하는 표현이 포함되지 않았는가?
[ ] theology.yaml의 저자 신학 입장과 상충하는 내용이 없는가?
[ ] 저자가 사용하지 않는 신학 용어나 표현이 사용되지 않았는가?
[ ] (sermon_collection/commentary) sermon_pattern.yaml 구조가 반영되었는가?
```

불일치 발견 시: 해당 부분을 수정하여 프로필과 일치시킨 후 저장한다.

### Step 5: 개정판 모드 (revision)

`type: revision`인 경우 Step 3 대신 다음 절차를 따른다.

```
원본 문서 로드 (project.yaml의 base_document 경로)
  ↓
섹션별로 분할하여 순차 처리
  ↓
각 섹션마다:
  1. wiki/ 검색 — 해당 주제의 최신 KB 상태 확인
  2. 원본 내용과 KB 비교 → 업데이트/보완 필요 부분 식별
  3. 변경 제안 목록 생성 (추가할 내용, 수정할 내용, 삭제할 내용)
  4. 사용자에게 변경 제안 제시 → 승인 받기
  5. 승인된 내용만 수정하여 drafts/에 저장
  ↓
전체 섹션 완료 후 완료 리포트
```

개정판 모드에서도 Step 4 자기 검증을 각 섹션마다 적용한다.

### Step 6: 초안 저장 및 완료 리포트

**챕터 완료 시 컨텍스트 정리:**

각 챕터 초안을 파일로 저장한 직후:
1. 챕터 내용을 5-10줄로 요약 생성 ("챕터 N 요약: ...")
2. 챕터 원문은 컨텍스트에서 제거 (파일에 저장됨)
3. 요약만 컨텍스트에 유지하여 다음 챕터 집필 시 연속성 확보

**저장 형식:**

```
projects/{project_name}/drafts/
└── {draft_file}   # project.yaml outline의 draft_file 값 사용. 예: ch01_로마서의_배경.md
```

**draft_file 생성 규칙:**
- `slug` = `ch{번호(2자리 0패딩)}_{제목 sanitized}` (예: "1장: 로마서의 배경" → `ch01_로마서의_배경`)
  - sanitize: 공백 → `_`, 특수문자 제거, 한글·영문·숫자·언더스코어만 허용
- `draft_file` = `{slug}.md`
- project.yaml outline 각 항목에 `slug`와 `draft_file`을 기록하고, 반드시 해당 파일명으로 drafts/에 저장한다

각 초안 파일의 상단에 다음 프론트매터를 포함한다:

```yaml
---
project: "{project_name}"
chapter: {번호}
title: "{챕터 제목}"
status: draft
created: {날짜}
wiki_sources:
  - "{참조한 wiki 기사 경로}"
---
```

**완료 리포트:**

```
집필 완료 리포트

프로젝트: {project_name}
유형: {type}
작성된 챕터: {N}개
총 분량: 약 {M}자
저장 위치: projects/{project_name}/drafts/

챕터별 현황:
  ch01 - {제목}: ✓ 완료
  ch02 - {제목}: ✓ 완료
  ...

wiki 참조 기사: {K}개
자기 검증: 통과

다음 단계:
초안을 검토하고 교정하려면 /publish-review를 실행하세요.
```

---

## 커스텀 집필 모드

`publish-write/references/custom-modes.md` 파일이 존재하면 **공통 writing-modes에 추가**로 적용한다.
커스텀 모드에는 특정 사용자/교회에 맞는 집필 유형을 정의할 수 있다:
- 주보 칼럼 모드
- 교회 뉴스레터 모드
- 특정 시리즈물 템플릿

## 참고자료 사용 원칙

위키의 `references/` 기사와 `type: reference` 원문은 목사님의 글이 아니다.

- 참고자료는 **출처를 밝힌 인용이나 요약**으로만 쓴다. 예: "○○의 『△△』에 따르면 …"
- 참고자료의 주장·해석을 목사님의 신학적 입장이나 고백, 문장으로 바꿔 쓰지 않는다.
  목사님의 입장은 `type: primary` 원고와 그로부터 만든 위키 기사에서만 가져온다.
- 문체(어미·호칭·리듬·설교 구조)는 오직 설교 팩(primary 원고 기반)을 따른다.
  참고자료의 문체를 흉내 내지 않는다.
- 참고자료와 목사님 입장이 다르면 둘을 섞지 말고, 목사님 입장을 본문으로 두고
  참고자료는 비교 자료로 밝혀 둔다.

## 설교 팩 (Sermon Pack)

`authors/{author_id}/sermon-pack.md`가 존재하면(설교집/강해서 모드),
Step 2 프로필 로드에 이어 이 팩을 **집필 제약**으로 함께 로드한다. 6섹션
(레지스터/시그니처/리듬/설교 구조 관습/대조페어/Do-NOT)의 지침을 초안 작성
전체에 반영한다. `custom-sermon-pack.md`가 있으면 그 파일이 우선한다.

챕터(또는 설교문) 초안 완료 후, Step 4 자기 검증에 이어 기계 게이트를 돌린다
(워크스페이스에서 실행):

```
python3 "{skill_root}/shared/scripts/verify_sermon.py" <초안 파일> \
  --fingerprint authors/{author_id}/sermon-fingerprint.json \
  --rules authors/{author_id}/sermon-rules.json
```

`{skill_root}` = 이 스킬이 설치된 디렉토리 (일반적으로 `~/.claude/skills/publish-agent`;
리포에서 직접 쓸 때는 `<repo>/skills`). Windows에서는 `python3` 대신 `py -3` 사용.

- `ok:true` → 통과, 정상 진행.
- `ok:false` → 위반 목록(check/expected/actual/evidence)을 근거로 해당 부분을
  재작성한다. **최대 2회**까지 재시도.
- 2회 재작성 후에도 `ok:false`이면 재작성을 멈추고, 남은 위반 목록을 있는
  그대로 사용자에게 보고한다 (통과한 것처럼 감추지 않는다).

sermon-pack.md/sermon-rules.json이 없으면 이 절차를 건너뛰고 기존 자기 검증
체크리스트만 수행한다.

## 참조 문서

- `shared/references/search-strategy.md` — wiki/ 계층적 요약 검색 전략
- `shared/references/workspace-schema.md` — project.yaml 스키마 + 워크스페이스 구조
- `shared/references/author-profile-schema.md` — 저자 프로필 4파일 스키마
- `shared/references/context-management.md` — 컨텍스트 윈도우 관리 전략 + 챕터별 토큰 예산
- `shared/references/sermon-pack-schema.md` — 설교 팩(sermon-pack.md/sermon-rules.json) 스키마
- `publish-write/references/writing-modes.md` — 프로젝트 유형별 상세 가이드 (공통)
- `publish-write/references/custom-modes.md` — 사용자별 추가 집필 모드 (있으면 추가 적용)
- proposal.md (프로젝트 디렉토리 내) — 기획 의도·독자·메시지 맥락 (집필 방향 참조용)
