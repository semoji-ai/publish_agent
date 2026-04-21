# Publish Agent — 설계 문서

> 저자의 기존 저서·설교·글을 분석하여 개인 신학 위키(KB)를 구축하고,
> 저자의 문체·신학관·설교구조를 완전히 습득한 상태에서
> 새 책 집필, 기존 책 개정, 설교 준비를 지원하는 LLM 스킬 시스템.

**작성일:** 2026-04-21
**최종 수정:** 2026-04-22
**대상 사용자:** 목사, 신학자, 기독교 저술가
**플랫폼:** Claude Code, Codex (OpenAI), Gemini CLI

---

## 1. 핵심 개념

### 1.1 옵시디언 볼트 + LLM Wiki 하이브리드

수집된 자료를 단순 저장하지 않고, LLM Wiki(Andrej Karpathy 방식)의 **흡수(absorption)** 패턴으로 의미 있는 위키 기사로 컴파일한다.

- **옵시디언 볼트** — 위키링크(`[[구원론]]`)로 지식 간 연결, 파일 기반, 사람이 읽고 탐색 가능
- **LLM Wiki** — 요약 레이어 + 청킹으로 LLM이 토큰 효율적으로 탐색 가능
- **이중 검색 구조** — 토픽 인덱스(사람용 브라우징) + 계층적 요약 검색(LLM용 시멘틱 검색)

### 1.2 허브 & 스포크 아키텍처

KB는 두 영역으로 구성된다: **wiki/** (지식 기사)와 **authors/** (저자 프로필). 모든 스킬이 이 두 영역을 읽고/쓰며, 저자 프로필이 일관성의 기준이 된다.

```
/publish-setup    → config.yaml + 디렉토리 구조 초기화
                        ↓
/publish-collect  → raw/entries/
                        ↓
/publish-absorb   → wiki/ (지식 기사)
                        ↓
/publish-profile  → authors/ (저자 프로필)
                        ↓
              ┌─────────┼─────────┐
              ↓         ↓         ↓
      /publish-write  /publish-sermon  /publish-curate
              ↓
      /publish-review (wiki/ + authors/ 기반 심사)
              ↓
      /publish-export
```

### 1.3 저자 프로필 기반 일관성

심사(/publish-review)는 "일반적 글쓰기 규칙"이 아닌 **"이 저자의 신학적 입장, 가치관, 문체와 일치하는가"**를 기준으로 판단한다. 각 목사님의 신학적 관점 차이를 존중한다.

---

## 2. 스킬 구성

총 9개 스킬. 온보딩(Phase 1)에서는 대화형 가이드가 순서대로 스킬을 안내하고, 일상 사용(Phase 2)에서는 LLM이 대화 맥락에서 적절한 스킬을 자동 호출한다. 사용자가 슬래시 명령어를 암기할 필요 없다.

| # | 스킬 | 역할 | KB 관계 |
|---|------|------|---------|
| 0 | `/publish-setup` | 워크스페이스 초기화, 저자 기본 정보 | KB 생성 |
| 1 | `/publish-collect` | 로컬/웹 자료 수집 (1차·2차 자료) | raw 쓰기 |
| 2 | `/publish-absorb` | raw entries → 위키 기사 흡수 | KB 쓰기 |
| 3 | `/publish-profile` | 저자 프로필 분석/갱신 | KB 읽기+쓰기 |
| 4 | `/publish-write` | KB + 프로필 기반 집필 (신규/개정) | KB 읽기 |
| 5 | `/publish-review` | KB + 프로필 기반 교정/심사 | KB 읽기 |
| 6 | `/publish-curate` | KB 검수/오염 제거/롤백 | KB 읽기+쓰기 |
| 7 | `/publish-export` | Markdown → DOCX/PDF/ePub 변환 | 읽기만 |
| 8 | `/publish-sermon` | 설교 준비용 KB 조회 | KB 읽기 |

---

## 3. 라이프사이클

### Phase 1: 온보딩 (초기 1회)

스킬 설치 후 첫 시운전. 대화형으로 가이드한다.

```
1. /publish-setup   — 워크스페이스 경로 지정, 저자 기본 정보 입력
2. /publish-collect — 기존 자료 일괄 수집 (경로/URL 지정)
3. /publish-absorb  — 전체 KB 구축 (대량 배치, 15건씩 체크포인트)
4. /publish-profile — 저자 프로필 최초 생성
→ "나만의 신학 위키" 준비 완료
```

### Phase 2: 일상 사용

사용자는 자연어로 대화만 하면 LLM이 적절한 스킬을 내부 호출.

| 의도 | 호출 스킬 |
|------|-----------|
| 새 자료 추가 | collect → absorb (증분) |
| 새 책 집필 | write → review → export |
| 기존 책 개정 | write(개정 모드) → review → export |
| 설교 준비 | sermon |
| KB 정리/오류 수정 | curate |
| 프로필 갱신 | profile |

---

## 4. 워크스페이스 구조

```
{workspace}/
├── config.yaml                     # 워크스페이스 설정 (아래 4.0 참조)
├── authors/
│   └── {author_id}/
│       ├── theology.yaml           # 신학적 입장 (구원론, 종말론 등)
│       ├── style.yaml              # 문체 (어투, 문장구조, 수사법)
│       ├── sermon_pattern.yaml     # 설교 구조 패턴
│       └── vocabulary.md           # 자주 쓰는/피하는 표현
├── wiki/                           # LLM Wiki (옵시디언 호환)
│   ├── _index.md                   # 마스터 인덱스 (전체 기사 목록 + 한줄 요약)
│   ├── _backlinks.json             # 역링크 그래프 (아래 4.4 참조)
│   ├── _absorb_log.json            # 흡수 이력 추적 (아래 4.5 참조)
│   ├── people/                     # 인물 (신학자, 성경인물)
│   │   ├── _index.md               # 카테고리별 인덱스
│   │   └── {article_name}/         # 기사 디렉토리 (2-tier)
│   │       ├── index.md            # 기사 본문 (요약 포함)
│   │       └── chunks/             # 상세 청크
│   ├── concepts/                   # 개념 기사 (구원론, 은혜, 언약)
│   │   └── _index.md
│   ├── sermons/                    # 설교별 기사
│   │   └── _index.md
│   ├── books/                      # 저서별 기사
│   │   └── _index.md
│   ├── passages/                   # 성경 본문별 기사 (단락/본문 단위)
│   │   └── _index.md
│   └── references/                 # 참고자료 기사
│       └── _index.md
├── raw/
│   └── entries/                    # 수집된 원본 (정제된 마크다운)
│       └── {date}_{source_id}.md
├── projects/
│   └── {project_name}/
│       ├── project.yaml            # 프로젝트 설정 (아래 4.6 참조)
│       ├── drafts/                 # 초안
│       ├── reviews/                # 심사 리포트
│       └── exports/                # 최종 출력물
├── snapshots/                      # 롤백용 스냅샷 (아래 4.7 참조)
└── logs/                           # 수집/분석/심사 이력
```

### 4.0 config.yaml 스키마

```yaml
workspace:
  name: "김목사 서재"
  created: 2026-04-21
  version: 1

author:
  id: "kim_pastor"              # 디렉토리명으로 사용
  name: "김철수"
  denomination: "대한예수교장로회"  # 선택
  role: "담임목사"                # 선택

defaults:
  source_type: primary           # 수집 시 기본 자료 유형
  batch_size: 15                 # absorb 배치 크기 (조절 가능)
  review_max_rounds: 3           # 심사 루프 최대 횟수
  encoding: utf-8                # 입력 파일 인코딩 (utf-8 | euc-kr | auto)

export:
  pandoc_path: pandoc            # pandoc 경로 (setup 시 존재 확인)
```

### 4.1 위키 기사 포맷 (2-tier 구조)

**모든 위키 기사는 디렉토리 기반 2-tier 구조를 사용한다.**

```
wiki/concepts/구원론/
├── index.md          # 기사 본문 (상단 요약 필수 포함)
└── chunks/           # 원문 기반 상세 섹션
    ├── 001.md
    └── 002.md
```

`index.md` 포맷 (옵시디언 호환):

```markdown
---
title: 구원론
type: concept
created: 2026-04-21
updated: 2026-04-21
summary: "저자는 개혁주의 구원론에 기반하되 은혜의 무조건성을 강조하며..."
related:
  - "[[은혜]]"
  - "[[칭의]]"
  - "[[성화]]"
sources:
  - src_20260421_001
  - src_20260421_015
tags:
  - 조직신학
  - 구원
chunk_count: 2
---

# 구원론

> **요약:** 저자는 개혁주의 구원론에 기반하되 은혜의 무조건성을 강조하며...

{저자의 구원론적 입장과 관련 내용을 테마별로 조직}

## 저자의 핵심 입장

...

## 관련 설교

- [[2024_부활절_설교]] — 은혜의 무조건성 강조
- [[2023_로마서_강해_3]] — 칭의와 성화의 관계

## 관련 저서

- [[믿음의 여정]] 3장 — 구원론 체계 정리

## Backlinks
```

**LLM 검색 흐름:**
1. 루트 `wiki/_index.md` 또는 카테고리 `_index.md` 스캔 (제목 + 한줄 요약)
2. 관련 기사 `index.md`의 `summary` 필드 또는 상단 요약 블록 읽기
3. 필요한 `chunks/`만 로드

**카테고리 `_index.md` 예시:**
```markdown
# Concepts Index

- [[구원론]] — 개혁주의 구원론, 은혜의 무조건성 강조
- [[은혜]] — 칭의적 은혜와 성화적 은혜 구분
- [[언약]] — 은혜 언약 중심, 행위 언약과의 관계
```

KB가 커지면 루트 `_index.md` 대신 **카테고리별 `_index.md`를 먼저 스캔**하여 토큰 효율 유지.

### 4.2 raw entry 포맷

```markdown
---
source_id: src_20260421_001
batch_id: batch_20260421
type: primary | reference
category: sermon | book | essay | commentary | thesis | article
title: "제목"
author: "저자"
source_url: ""
source_path: ""
ingested_at: 2026-04-21
confidence: high | medium | low
content_hash: "sha256:..."       # 중복 감지용
tags: []
absorbed: false
deleted: false
---

{정제된 원문 내용}
```

`content_hash` 필드로 동일 자료 중복 수집 방지 (같은 설교가 블로그 + 로컬 파일로 수집될 경우).

### 4.3 absorb 매칭 로직

기존 기사와 새 항목의 매칭 기준:

1. **제목/주제 매칭** — 새 항목의 제목·핵심 주제와 기존 기사 제목 비교
2. **위키링크 중첩** — 새 항목에서 추출한 키워드가 기존 기사의 tags/related와 겹치는 정도
3. **카테고리 일치** — 같은 카테고리(concepts, sermons 등) 내 기사 우선 검토
4. **LLM 판단** — 위 기준으로 후보 2-3개 선정 후 LLM이 "병합 vs 신규 생성" 최종 결정

**분리 기준 (Anti-cramming):** 기존 기사가 200줄 이상이고, 새 내용이 기존 기사의 하위 주제로 독립 가능하면 별도 기사로 분리.
**최소 기준 (Anti-thinning):** 기사 최소 15줄. 그 미만이면 관련 기사에 병합.

### 4.4 _backlinks.json 스키마

```json
{
  "구원론": ["은혜", "칭의", "로마서_강해_3", "믿음의_여정"],
  "은혜": ["구원론", "2024_부활절_설교", "요한복음_1장"]
}
```

키: 기사명, 값: 해당 기사를 `[[링크]]`하는 다른 기사명 배열.
absorb/curate 실행 시 자동 재구축.

### 4.5 _absorb_log.json 스키마

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
    }
  ],
  "pending_entries": []
}
```

**중단 재개:** `status: "in_progress"`인 배치가 있으면 `pending_entries`에서 미처리 항목부터 이어서 진행. 이미 처리된 항목(absorbed: true)은 건너뜀.

### 4.6 project.yaml 스키마

```yaml
name: "로마서 강해"
type: new_book | revision | sermon_collection | commentary
author_id: "kim_pastor"
created: 2026-04-21
status: drafting | reviewing | exported

outline:
  - title: "1장: 로마서의 배경"
    status: draft | review | done
  - title: "2장: 의의 계시"
    status: pending

base_document: ""               # 개정판일 경우 원본 경로
wiki_queries:                    # 이 프로젝트에서 참조할 주요 토픽
  - "로마서"
  - "칭의"
  - "율법과 복음"
```

### 4.7 스냅샷 메커니즘

```
snapshots/
└── 2026-04-21T140000/
    ├── manifest.json            # 스냅샷 메타데이터
    ├── wiki/_index.md           # 인덱스 사본
    └── wiki/_backlinks.json     # 백링크 사본
```

**manifest.json:**
```json
{
  "created_at": "2026-04-21T14:00:00",
  "trigger": "pre_absorb | manual | pre_curate",
  "batch_id": "batch_20260421",
  "article_count": 150,
  "description": "absorb 45건 실행 전 스냅샷"
}
```

- **자동 스냅샷:** absorb, curate 실행 전 자동 생성
- **수동 스냅샷:** 사용자 요청 시
- **롤백:** 스냅샷의 인덱스/백링크 복원 + 해당 batch의 기사 변경 되돌리기 (soft delete된 항목 복구 포함)

---

## 5. 스킬별 상세 워크플로우

### 5.0 `/publish-setup`

**트리거:** 스킬 최초 사용 시, "워크스페이스 만들어줘", "publish agent 설정"

```
사용자 입력: 워크스페이스 경로, 저자명
  ↓
의존성 확인 (pandoc 설치 여부 체크, 미설치 시 안내)
  ↓
워크스페이스 디렉토리 구조 생성 (전체 트리)
  ↓
config.yaml 초기화 (저자 정보, author_id 자동 생성)
  ↓
authors/{author_id}/ 디렉토리 + 빈 프로필 파일 생성
  ↓
빈 wiki/_index.md, 카테고리별 _index.md, _backlinks.json 생성
  ↓
완료 리포트
```

### 5.1 `/publish-collect`

**트리거:** "자료 수집해줘", "이 파일들 분석해줘", "이 URL에서 가져와", 새 자료 추가 요청

**수집 범위:**

- **1차 자료 (primary):** 저자 본인 저서, 설교문, 원고, 블로그 글
- **2차 자료 (reference):** 신학 논문, 주석서, 성경 사전, 원어 자료, 타 목사/신학자 공개 설교·저서, 일반 도서·문헌

```
사용자 입력: 파일 경로/URL/디렉토리 + 자료 유형(primary|reference)
  ↓
파일 형식 감지 (md, txt, docx, pdf, html)
  ↓
인코딩 감지 + UTF-8 정규화
  ↓
content_hash 계산 → 중복 체크
  ↓
마크다운 변환 + YAML 프론트매터 부여
  ↓
primary/reference 태그 구분
  ↓
raw/entries/{date}_{source_id}.md 저장
  ↓
수집 리포트 (N건 수집, M건 중복 건너뜀, 형식별·유형별 분류)
```

### 5.2 `/publish-absorb`

**트리거:** collect 완료 후 자동, "위키 업데이트해줘", "자료 정리해줘"

```
raw/entries/ 스캔 (absorbed: false 항목 탐지)
  ↓
배치 단위 처리 (15건씩)
  ↓
각 항목마다:
  1. 원본 읽기 → "이것이 무엇을 의미하는가?" 분석
  2. _index.md 스캔 → 기존 기사 매칭
  3. 매칭됨 → 기존 기사 재읽기 → 병합 업데이트
     매칭 안 됨 → 새 기사 생성
  4. 패턴 인식 → 개념 기사(concepts/) 생성/갱신
  5. 위키링크 + 백링크 업데이트
  6. 요약(summary) + 청크(chunks/) 생성
  ↓
배치마다 체크포인트 (_absorb_log.json)
  ↓
_index.md 재구축
  ↓
absorbed: true 마킹
  ↓
흡수 리포트 (N건 처리, 기사 M개 생성/갱신)
```

**Anti-cramming:** 기존 큰 기사에 무분별하게 추가하지 않음. 하위 주제가 성장하면 분리.
**Anti-thinning:** 너무 작은 스텁 생성 금지. 최소 15줄 이상.

### 5.3 `/publish-profile`

**트리거:** 온보딩 시, "내 문체 분석해줘", "프로필 업데이트", 대량 자료 추가 후

```
사용자 입력: 분석 대상 (전체 | 특정 자료)
  ↓
wiki/ 기사들 + raw/entries/ 원본 샘플링
  ↓
병렬 분석:
  ├── 문체 분석 → style.yaml
  │   (어투, 문장 길이, 수사법, 비유 패턴, 논증 구조)
  ├── 신학적 입장 → theology.yaml
  │   (구원론, 종말론, 교회론, 성령론, 성경관 등)
  ├── 설교 구조 → sermon_pattern.yaml
  │   (귀납/연역/내러티브, 도입-본론-적용 비율, 예화 빈도)
  └── 어휘 패턴 → vocabulary.md
      (자주 쓰는 표현, 피하는 표현, 성경 인용 방식)
  ↓
기존 프로필과 diff → 변경점 사용자에게 제시
  ↓
승인 시 프로필 갱신
```

### 5.4 `/publish-write`

**트리거:** "책 써줘", "3장 초안", "개정판 수정해줘", "설교집 정리해줘"

```
사용자 입력: 프로젝트 유형(신규 책|개정판|설교집|강해서) + 주제/목차
  ↓
projects/{name}/project.yaml 생성
  ↓
wiki/ 계층 검색 (index → summary → chunks)
  ↓
저자 프로필 로드 (style + theology + sermon_pattern + vocabulary)
  ↓
챕터별 초안 작성 → drafts/
  ↓
자기 검증 (프로필 대비 문체/관점 일치도 체크)
  ↓
초안 완료 리포트
```

**개정판 모드:** 기존 원고를 로드 → KB 최신 상태와 비교 → 업데이트/보완 제안 → 수정.

### 5.5 `/publish-review`

**트리거:** 초안 완료 후 자동, "검토해줘", "교정해줘", "심사해줘"

```
사용자 입력: 심사 대상 (drafts/ 내 파일)
  ↓
저자 프로필 로드 (전체)
  ↓
wiki/ 관련 기사 참조 (KB 기반 심사)
  ↓
4차원 심사:
  ├── 문체 일관성 (style.yaml + vocabulary.md 대비)
  ├── 신학적 일관성 (theology.yaml 대비 — 저자의 관점 기준)
  ├── 논리 구조 / 설득력 / 독자 적합성
  └── 문법 / 맞춤법 / 가독성
  ↓
심사 리포트 → reviews/{date}_review.md
  ↓
사용자 확인 → 승인된 수정사항 반영
  ↓
재심사 루프:
  - 자동 재심사로 개선 확인
  - 최대 3회 (config.yaml의 review_max_rounds)
  - 3회 후에도 미해결 이슈 있으면 사용자에게 판단 위임
  - 각 라운드는 사용자 승인 후 실행
```

**핵심:** 신학적 검증은 "절대적 정답" 기준이 아니라 **해당 저자의 신학적 입장과의 일관성** 기준.

**Soft delete 정의:** `deleted: true` 플래그를 프론트매터에 설정. 파일은 유지되나 `_index.md`에서 제외되고, 검색·absorb·review 대상에서 제외됨. `curate`에서 복구(deleted: false) 가능.

### 5.6 `/publish-curate`

**트리거:** "위키 정리해줘", "잘못된 자료 있는지 확인", "이 배치 롤백"

```
사용자 입력: 검수 범위 (전체 | 특정 배치 | 특정 출처)
  ↓
저자 프로필 기준 이질성 스캔
  ↓
플래그된 항목 리포트 (이유 + 출처 표시)
  ↓
사용자 선택: 개별 삭제 | 배치 롤백 | 무시
  ↓
실행 (soft delete) + 스냅샷 갱신
  ↓
_index.md, _backlinks.json 재구축
```

**버전 관리:**
- 모든 KB 항목에 `source_id`, `ingested_at`, `batch_id` 부여
- 특정 배치 단위 통째로 롤백 가능
- 삭제는 soft delete → 복구 가능
- snapshots/ 디렉토리에 주요 시점 스냅샷 보관

### 5.7 `/publish-export`

**트리거:** "PDF로 만들어줘", "출판용 파일 만들어줘", "ePub으로 변환"

```
사용자 입력: 대상 프로젝트 + 출력 포맷 (DOCX|PDF|ePub)
  ↓
drafts/ 최종본 취합 + 목차 구성
  ↓
pandoc 또는 동등 도구로 변환
  ↓
exports/{format}/ 저장
  ↓
완료 리포트 (파일 경로)
```

### 5.8 `/publish-sermon`

**트리거:** "설교 준비 도와줘", "요한복음 3장에 대해 내가 뭐라고 했지?", "은혜에 대한 자료 찾아줘"

```
사용자 입력: 자연어 질문 또는 성경 본문
  ↓
wiki/ 계층 검색 (index → summary → chunks)
  ↓
관련 기사 종합:
  ├── 저자 과거 설교 요약
  ├── 저자의 해당 주제 입장 (concepts/)
  ├── 관련 성경 본문 기사 (passages/)
  └── 참고자료 (references/)
  ↓
설교 준비 자료 제시
```

---

## 6. 시멘틱 검색 전략

별도 임베딩 API 없이, 구독제 LLM 자체를 검색 엔진으로 활용한다.

### 계층적 요약 검색

```
Level 0: _index.md (전체 기사 제목 + 한줄 요약)     ← 토큰 최소
Level 1: 각 기사 index.md 상단 요약                   ← 필요 시
Level 2: chunks/ 상세 내용                             ← 정말 필요한 것만
```

**검색 품질은 absorb 시 요약 품질에 의존.** 요약이 해당 기사의 핵심을 정확히 포착해야 한다.

### v2 검색 품질 개선 옵션 (추후)

- 임베딩 기반 벡터 검색
- 옵시디언 Smart Connections 플러그인 연동
- 그래프 기반 관련도 스코어링

---

## 7. 플랫폼 호환성

### 원칙

- SKILL.md는 플랫폼 중립적 워크플로우로 작성
- 도구 호출 부분만 플랫폼별 매핑

### 도구 매핑

도구명은 각 플랫폼의 실제 API에 따라 구현 시 검증 필요 (TBD 표시).

| 기능 | Claude Code | Codex (TBD) | Gemini CLI (TBD) |
|------|-------------|-------------|-------------------|
| 파일 읽기 | Read | TBD | TBD |
| 파일 쓰기 | Write | TBD | TBD |
| 파일 편집 | Edit | TBD | TBD |
| 검색 | Grep/Glob | TBD | TBD |
| 셸 실행 | Bash | TBD | TBD |
| 웹 가져오기 | WebFetch | TBD | TBD |
| 멀티에이전트 | Agent | 미지원 (순차 처리로 대체) | 미지원 (순차 처리로 대체) |

**Agent 도구 비호환 대응:** Claude Code의 Agent(병렬 서브에이전트)는 Codex/Gemini에 동등 기능 없음. 해당 플랫폼에서는 동일 워크플로우를 순차 처리로 실행. SKILL.md에서 병렬 처리는 "가능한 경우" 조건부로 기술.

### 참고 문서

각 스킬의 `references/` 디렉토리에 플랫폼별 도구 매핑 가이드 포함:
- `references/platform-tools.md` — 구현 시 각 플랫폼 문서 기반으로 작성

---

## 8. 데이터 입력 지원 형식

### 로컬 파일
- Markdown (.md)
- Plain text (.txt)
- Word (.docx)
- PDF (.pdf) — 텍스트 기반만 지원. 스캔(이미지) PDF는 사용자에게 OCR 후 재입력 안내

**미지원:** HWP (.hwp) — 안정적 오픈소스 파서 없음. 사용자가 DOCX/TXT로 변환 후 입력.

### 웹 소스
- 블로그 URL (브런치, 네이버블로그, 티스토리 등)
- 학술 DB (학술논문 URL)
- 웹 페이지 일반

**참고:** 일부 한국 블로그 플랫폼(네이버블로그 등)은 JavaScript 렌더링으로 인해 WebFetch로 내용 추출이 불완전할 수 있음. 이 경우 사용자가 해당 글을 복사하여 로컬 파일(.md/.txt)로 저장 후 수집 권장.

### 인코딩 처리

수집 시 파일 인코딩 자동 감지 (UTF-8, EUC-KR, CP949). config.yaml의 `defaults.encoding`으로 기본값 지정 가능.

### 에러 처리

| 상황 | 대응 |
|------|------|
| 파일 변환 실패 (손상된 DOCX/PDF) | 해당 파일 건너뛰기, 로그 기록, 사용자에게 리포트 |
| 중복 소스 감지 (content_hash 일치) | 기존 항목 참조 안내, 중복 수집 차단 |
| 웹 페이지 내용 추출 실패 | 수동 입력 권장, 로그 기록 |
| absorb 중 배치 중단 | _absorb_log.json 기반 자동 재개 (4.5 참조) |
| 옵시디언 동시 편집 충돌 | absorb/curate 실행 전 경고, 사용자에게 옵시디언 닫기 권장 |

---

## 9. 설계 원칙

1. **토큰 효율 최우선** — Markdown 기반 작업, 계층적 검색, 필요한 것만 로드
2. **저자 중심** — 모든 심사·생성이 저자 프로필 기준
3. **신학적 다양성 존중** — 절대적 교리 기준 없음, 저자의 입장과의 일관성만 검증
4. **누적형 KB** — 한 번 구축하면 계속 성장, 여러 프로젝트에서 재사용
5. **옵시디언 호환** — 사용자가 직접 KB를 탐색·편집 가능
6. **플랫폼 무관** — Claude Code, Codex, Gemini CLI 모두 지원
7. **추가 비용 없음** — 구독제 LLM만으로 모든 기능 작동
8. **대화형 UX** — 슬래시 명령어 암기 불필요, 자연어로 대화
