---
name: workspace-schema
description: Publish Agent 워크스페이스 구조 및 전체 YAML/JSON 스키마 정의. 모든 스킬이 참조하는 공통 구조 기준서.
---

# 워크스페이스 구조

## 디렉토리 트리

아래 트리는 `/publish-setup` 스킬이 초기화하는 전체 구조다. 모든 스킬은 이 구조를 기준으로 경로를 해석한다.

```
{workspace}/
├── config.yaml                     # 워크스페이스 전역 설정 (스키마 → 4.0)
├── authors/
│   └── {author_id}/                # author_id는 config.yaml에서 결정 (예: kim_pastor)
│       ├── theology.yaml           # 신학적 입장 (구원론, 종말론, 교회론, 성령론, 성경관)
│       ├── style.yaml              # 문체 (어투, 문장 길이, 수사법, 논증 방식)
│       ├── sermon_pattern.yaml     # 설교 구조 패턴 (귀납/연역, 구성 비율, 예화 빈도)
│       └── vocabulary.md          # 자주 쓰는/피하는 표현, 성경 인용 방식
├── wiki/                           # LLM Wiki (옵시디언 볼트 호환)
│   ├── _index.md                   # 마스터 인덱스 — 전체 기사 제목 + 한줄 요약 목록
│   ├── _backlinks.json             # 역링크 그래프 — 기사 간 [[링크]] 관계 (스키마 → 4.4)
│   ├── _absorb_log.json            # 흡수 이력 — 배치 처리 상태 추적 (스키마 → 4.5)
│   ├── people/                     # 인물 기사 (신학자, 성경 인물, 저자)
│   │   ├── _index.md               # people 카테고리 인덱스
│   │   └── {article_name}/         # 기사 디렉토리 (2-tier 구조)
│   │       ├── index.md            # 기사 본문 (요약 블록 필수 포함)
│   │       └── chunks/             # 상세 섹션 청크 (001.md, 002.md, ...)
│   ├── concepts/                   # 개념 기사 (구원론, 은혜, 언약, 칭의 등)
│   │   ├── _index.md               # concepts 카테고리 인덱스
│   │   └── {article_name}/
│   │       ├── index.md
│   │       └── chunks/
│   ├── sermons/                    # 설교별 기사 (개별 설교 기록/분석)
│   │   ├── _index.md               # sermons 카테고리 인덱스
│   │   └── {article_name}/
│   │       ├── index.md
│   │       └── chunks/
│   ├── books/                      # 저서별 기사 (저자의 출판물, 참고 도서)
│   │   ├── _index.md               # books 카테고리 인덱스
│   │   └── {article_name}/
│   │       ├── index.md
│   │       └── chunks/
│   ├── passages/                   # 성경 본문별 기사 (단락/본문 단위)
│   │   ├── _index.md               # passages 카테고리 인덱스
│   │   └── {article_name}/
│   │       ├── index.md
│   │       └── chunks/
│   └── references/                 # 참고자료 기사 (신학 논문, 주석서, 외부 자료)
│       ├── _index.md               # references 카테고리 인덱스
│       └── {article_name}/
│           ├── index.md
│           └── chunks/
├── raw/
│   └── entries/                    # 수집된 원본 자료 (정제된 마크다운, YAML 프론트매터 포함)
│       └── {YYYYMMDD}_{source_id}.md   # 파일명 형식: 날짜_소스ID
├── plans/                         # 기획안 저장소 (/publish-plan이 관리)
│   └── plan_{id}/                 # 기획안별 디렉토리 (id: 사용자 지정)
│       ├── plan.yaml              # 기획 상태 + 구조화 데이터 (스키마 → 4.8)
│       ├── proposal.md            # 기획서 문서 (사람용, 인터뷰 진행 시 자동 갱신)
│       └── interview_log.md       # 소크라테스 인터뷰 누적 기록
├── projects/                       # 집필 프로젝트
│   └── {project_name}/
│       ├── project.yaml            # 프로젝트 설정 (스키마 → 4.6)
│       ├── drafts/                 # 챕터별 초안 마크다운
│       ├── reviews/                # 심사 리포트 ({date}_review.md)
│       └── exports/                # 최종 출력물 (DOCX, PDF, ePub)
│           ├── docx/
│           ├── pdf/
│           └── epub/
├── snapshots/                      # 롤백용 스냅샷 (absorb/curate 전 자동 생성)
│   └── {YYYY-MM-DDTHHMMSS}/        # 타임스탬프 디렉토리
│       ├── manifest.json           # 스냅샷 메타데이터 (스키마 → 4.7)
│       ├── wiki/_index.md          # 인덱스 사본
│       └── wiki/_backlinks.json    # 백링크 사본
└── logs/                           # 수집/분석/심사 이력 로그
```

---

## 4.0 config.yaml 스키마

워크스페이스 루트에 위치하는 전역 설정 파일. `/publish-setup` 이 초기화하며 모든 스킬이 참조한다.

```yaml
workspace:
  name: "김목사 서재"          # 워크스페이스 표시 이름 (자유 형식)
  created: 2026-04-21          # 초기화 날짜 (ISO 8601 날짜)
  version: 1                   # 스키마 버전 (현재 1)

author:
  id: "kim_pastor"             # authors/ 디렉토리명으로 사용. 영숫자+언더스코어 권장
  name: "김철수"               # 저자 표시 이름
  denomination: "대한예수교장로회"  # 교단 (선택. 미기입 시 빈 문자열)
  role: "담임목사"              # 직분/역할 (선택. 미기입 시 빈 문자열)

defaults:
  source_type: primary         # 수집 시 기본 자료 유형 (primary | reference)
  batch_size: 15               # absorb 배치 크기. 1-50 사이 정수. 메모리 한계 시 줄임
  review_max_rounds: 3         # 심사 루프 최대 반복 횟수 (1-5 사이 정수 권장)
  encoding: auto               # 입력 파일 기본 인코딩 (utf-8 | euc-kr | auto). Windows에서는 반드시 auto 권장 (CP949 자동 감지)

export:
  pandoc_path: pandoc          # pandoc 실행 경로. 시스템 PATH에 있으면 'pandoc'으로 충분
```

**필드 설명:**
- `author.id`: 자동 생성 규칙 — 저자 이름을 소문자 영문으로 변환 + 역할 축약어 결합 (예: "김철수" + "목사" → `kim_pastor`). 충돌 시 숫자 접미사 추가.
- `defaults.encoding: auto`: 파일별 인코딩 자동 감지 시도, 실패 시 utf-8 가정.
- `export.pandoc_path`: 절대 경로 지정 가능 (예: `/usr/local/bin/pandoc`).

**경로 표기 규칙:**
- `workspace` 경로는 내부적으로 항상 `/` 구분자를 사용한다 (Windows에서도).
  - 올바른 예: `C:/Users/pastor/publish_workspace/`
  - 잘못된 예: `C:\Users\pastor\publish_workspace\`
- 사용자가 백슬래시로 경로를 입력하면 `/publish-setup`이 자동으로 슬래시로 변환하여 저장한다.

---

## 4.4 _backlinks.json 스키마

`wiki/_backlinks.json`에 위치. absorb 및 curate 실행 시 자동 재구축된다.

```json
{
  "구원론": ["은혜", "칭의", "로마서_강해_3", "믿음의_여정"],
  "은혜": ["구원론", "2024_부활절_설교", "요한복음_1장"],
  "칭의": ["구원론", "로마서_5장", "갈라디아서_강해"]
}
```

**구조 설명:**
- **키(key)**: 기사명 (wiki 디렉토리 내 `{article_name}`과 동일)
- **값(value)**: 해당 기사를 `[[기사명]]` 형식으로 링크하는 다른 기사명의 배열
- 기사가 삭제(soft delete)되면 해당 키와 값 배열에서 해당 항목을 제거
- 새 기사 생성/갱신 시 위키링크를 추출하여 이 파일에 반영

**재구축 규칙:**
1. wiki/ 하위 모든 `index.md` 파일을 스캔
2. 각 파일에서 `[[기사명]]` 패턴 추출
3. 추출된 링크를 대상 기사의 역링크 배열에 추가
4. `deleted: true`인 기사는 제외

---

## 4.5 _absorb_log.json 스키마

`wiki/_absorb_log.json`에 위치. absorb 진행 상태와 이력을 추적한다. 중단 재개(resume)의 핵심.

```json
{
  "last_batch_id": "batch_20260421",
  "last_processed_at": "2026-04-21T14:30:00",
  "batches": [
    {
      "batch_id": "batch_20260421",
      "started_at": "2026-04-21T14:00:00",
      "completed_at": "2026-04-21T14:30:00",
      "entries_total": 45,
      "entries_processed": 45,
      "articles_created": 12,
      "articles_updated": 8,
      "status": "completed"
    },
    {
      "batch_id": "batch_20260422",
      "started_at": "2026-04-22T09:00:00",
      "completed_at": null,
      "entries_total": 30,
      "entries_processed": 15,
      "articles_created": 4,
      "articles_updated": 3,
      "status": "in_progress"
    }
  ],
  "pending_entries": [
    "20260422_src_016.md",
    "20260422_src_017.md"
  ]
}
```

**필드 설명:**
- `last_batch_id`: 가장 최근 실행된 배치 ID
- `last_processed_at`: 마지막 항목 처리 시각 (ISO 8601)
- `batches[].batch_id`: 배치 식별자 (`batch_{YYYYMMDD}` 형식. 당일 복수 배치 시 `batch_{YYYYMMDD}_2` 등으로 구분)
- `batches[].status`: `"pending"` | `"in_progress"` | `"completed"` | `"failed"`
- `pending_entries`: 현재 `in_progress` 배치에서 아직 처리되지 않은 raw entry 파일명 목록

**중단 재개 로직:**
1. absorb 시작 시 `status: "in_progress"`인 배치 존재 여부 확인
2. 존재 시 `pending_entries`의 파일부터 이어서 처리
3. 각 항목 처리 완료 시 `entries_processed` 증가 + `pending_entries`에서 제거
4. `entries_processed === entries_total`이 되면 `status: "completed"`, `completed_at` 기록

---

## 4.6 project.yaml 스키마

`projects/{project_name}/project.yaml`에 위치. 집필 프로젝트의 메타데이터와 진행 상태를 관리한다.

```yaml
name: "로마서 강해"
type: new_book                  # new_book | revision | sermon_collection | commentary
author_id: "kim_pastor"         # config.yaml의 author.id와 일치해야 함
created: 2026-04-21             # 프로젝트 생성 날짜
status: drafting                # drafting | reviewing | exported

outline:
  - title: "1장: 로마서의 배경"
    slug: "ch01_로마서의_배경"       # 챕터 번호 + 제목을 sanitize하여 자동 생성
    draft_file: "ch01_로마서의_배경.md"  # drafts/ 하위 파일명. {slug}.md
    status: done                # draft | review | done | pending
  - title: "2장: 의의 계시"
    slug: "ch02_의의_계시"
    draft_file: "ch02_의의_계시.md"
    status: review
  - title: "3장: 죄의 보편성"
    slug: "ch03_죄의_보편성"
    draft_file: "ch03_죄의_보편성.md"
    status: drafting
  - title: "4장: 믿음으로 의롭다 함"
    slug: "ch04_믿음으로_의롭다_함"
    draft_file: "ch04_믿음으로_의롭다_함.md"
    status: pending

base_document: ""               # revision 타입일 경우 원본 파일 경로. 신규 작성 시 빈 문자열
wiki_queries:                   # 이 프로젝트에서 참조할 주요 위키 토픽 목록
  - "로마서"
  - "칭의"
  - "율법과 복음"
  - "바울 신학"
plan_id: ""                         # 원본 기획안 ID (plans/plan_{id}/ 참조). 기획 없이 생성된 경우 빈 문자열
summary:                            # publish-plan에서 생성된 기획 요약 (finalize 시 자동 생성)
  motivation: ""                    # 왜 이 책을 쓰는가
  core_question: ""                 # 이 책이 답하려는 질문
  audience: ""                      # 주 독자층 + 독자가 얻어갈 것
  thesis: ""                        # 핵심 주장/메시지
  key_themes: []                    # 핵심 주제 목록
flow_type: ""                       # 논리 전개 방식 (연역/귀납/내러티브 등)
```

**slug 생성 규칙:**
- 형식: `ch{번호(2자리 0패딩)}_{제목 sanitized}`
- sanitize: 공백 → `_`, 특수문자 제거, 한글·영문·숫자·언더스코어만 허용
- 예: "1장: 로마서의 배경" → `ch01_로마서의_배경`

**draft_file 규칙:**
- `{slug}.md` 형식 고정
- publish-write는 `drafts/{draft_file}` 경로에 초안을 저장해야 한다
- publish-export는 outline의 `draft_file` 필드로 drafts/ 파일을 찾아야 한다. draft_file이 누락된 항목이 있으면 사용자에게 경고한다

**타입별 의미:**
- `new_book`: 신규 도서 초안 작성
- `revision`: 기존 원고 개정 (`base_document` 필드에 원본 경로 필수)
- `sermon_collection`: 설교 모음집 편집 (wiki/sermons/ 기사 기반)
- `commentary`: 강해서 작성 (성경 본문 단위, wiki/passages/ 기반)

**outline.status 흐름:** `pending` → `drafting` → `draft` → `review` → `done`

**plan 연동 필드:**
- `plan_id`: publish-plan의 finalize로 생성된 경우 원본 기획안 ID. 기획 없이 생성된 기존 프로젝트는 빈 문자열. 하위 호환.
- `summary`: 기획 요약. publish-plan finalize 시 concept + audience + message에서 자동 생성. 없으면 빈 값으로 취급.
- `flow_type`: 기획에서 결정된 논리 전개 방식. 없으면 빈 문자열.

---

## 4.7 snapshots/manifest.json 스키마

`snapshots/{timestamp}/manifest.json`에 위치. 각 스냅샷의 생성 맥락과 범위를 기록한다.

```json
{
  "created_at": "2026-04-21T14:00:00",
  "trigger": "pre_absorb",
  "batch_id": "batch_20260421",
  "article_count": 150,
  "description": "absorb 45건 실행 전 스냅샷"
}
```

**필드 설명:**
- `created_at`: 스냅샷 생성 시각 (ISO 8601, 타임스탬프 디렉토리명과 동일)
- `trigger`: 생성 트리거
  - `"pre_absorb"`: absorb 실행 전 자동 생성
  - `"pre_curate"`: curate 실행 전 자동 생성
  - `"manual"`: 사용자 직접 요청
- `batch_id`: 이 스냅샷과 관련된 배치 ID (수동 생성 시 `null`)
- `article_count`: 스냅샷 시점의 전체 기사 수
- `description`: 사람이 읽을 수 있는 설명 (자동 생성 또는 사용자 입력)

**스냅샷 내용물:**
```
snapshots/{YYYY-MM-DDTHHMMSS}/
├── manifest.json           # 위 스키마
├── wiki/_index.md          # 스냅샷 시점의 마스터 인덱스 사본
└── wiki/_backlinks.json    # 스냅샷 시점의 역링크 그래프 사본
```

**롤백 절차:**
1. `snapshots/` 디렉토리 목록에서 롤백 대상 타임스탬프 선택
2. `manifest.json`의 `batch_id` 확인
3. 해당 batch_id로 생성/수정된 wiki 기사들을 soft delete 또는 이전 버전으로 복원
4. 스냅샷의 `_index.md`와 `_backlinks.json`을 `wiki/`에 복원
5. 해당 배치의 raw entries를 `absorbed: false`로 되돌림

---

## raw entry 스키마 (참고)

`raw/entries/{YYYYMMDD}_{source_id}.md` 프론트매터 구조. `/publish-collect` 스킬이 생성한다.

```yaml
---
source_id: src_20260421_001       # 소스 고유 ID (자동 생성)
batch_id: batch_20260421          # 수집 세션 배치 ID
type: primary                     # primary | reference
category: sermon                  # sermon | book | essay | commentary | thesis | article
title: "제목"
author: "저자"                     # primary 자료면 저자명, reference면 원저자
source_url: ""                    # 웹 수집 시 원본 URL
source_path: ""                   # 로컬 파일 수집 시 원본 경로
ingested_at: 2026-04-21           # 수집 날짜
confidence: high                  # 콘텐츠 추출 신뢰도: high | medium | low
content_hash: "sha256:abc123..."  # 정제된 본문의 SHA-256 해시 (중복 감지용)
tags: []                          # 수집 시 자동 부여 태그 (선택)
absorbed: false                   # absorb 완료 시 true로 변경
deleted: false                    # soft delete 시 true로 변경
parent_source_id: ""              # 대용량 파일 분할 시 원본 entry의 source_id. 분할 안 된 경우 빈 문자열
part: 0                           # 파트 번호 (0 = 분할 안 됨, 1부터 시작)
total_parts: 0                    # 전체 파트 수 (0 = 분할 안 됨)
part_title: ""                    # 이 파트의 제목 (감지된 경우)
---

{정제된 원문 내용 — 마크다운 형식}
```

**중복 감지:** 새 항목 수집 시 `content_hash`를 기존 raw/entries/ 전체와 비교. 동일한 해시가 존재하면 수집 차단 + 사용자에게 기존 항목 참조 안내.

**경로 필드 규칙:**
- `source_path`는 항상 `/` 구분자로 정규화하여 저장한다.
  - Windows 원본 경로가 `C:\Users\pastor\sermons\설교문.txt`이더라도 `C:/Users/pastor/sermons/설교문.txt`로 저장한다.
- `source_url`은 URL 형식이므로 `/`를 그대로 사용한다.

**분할 파일 필드 규칙 (대용량 파일 처리):**
- `parent_source_id`: 500줄 이상 파일이 분할된 경우, 각 파트 entry에 원본 source_id를 기록한다. 원본 entry 자체(`is_parent: true`)와 분할 안 된 단일 entry는 빈 문자열.
- `part` / `total_parts`: 분할된 경우 파트 순번과 총 파트 수를 기록한다. 분할 안 된 경우 모두 0.
- `part_title`: 분할점에서 감지된 챕터/섹션 제목. 없으면 빈 문자열.
- absorb 스킬은 `parent_source_id`가 비어 있지 않은 entry를 처리할 때 관련 파트들을 함께 고려하여 위키 기사를 구성할 수 있다.

---

## 4.8 plan.yaml 스키마

`plans/plan_{id}/plan.yaml`에 위치. `/publish-plan` 스킬이 생성·관리한다.

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

**status 흐름:** `concept` → `audience` → `message` → `structure` → `detail` → `finalized`

- `status`는 `interview.current_phase`와 동기화된다. phase가 전환되면 status도 함께 변경.
- finalize 실행 시 `status: finalized`로 변경되며 project로 변환 가능.

**plan_id 규칙:**
- 사용자가 지정하는 짧은 식별자 (예: `은혜론_2026`, `로마서강해`)
- 디렉토리명: `plans/plan_{id}/`
- sanitize: 공백 → `_`, 특수문자 제거, 한글·영문·숫자·언더스코어만 허용
