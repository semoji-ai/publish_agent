---
name: publish-absorb
description: Use when users say "/publish-absorb", "위키 업데이트해줘", "자료 정리해줘", "흡수해줘", "위키 만들어줘", or after collect is complete and the wiki needs to be updated from raw entries
---

# Publish Absorb — 위키 흡수

`raw/entries/`의 미흡수 항목을 분석하여 `wiki/` 기사로 컴파일한다. 이 스킬은 Publish Agent의 핵심 파이프라인으로, Andrej Karpathy의 LLM Wiki absorption 패턴을 사용한다. 단순 파일링이 아닌, 각 항목이 **무엇을 의미하는가**를 분석하여 성장하는 지식 위키를 구축한다.

## 트리거 조건

```
- "/publish-absorb"
- "위키 업데이트해줘"
- "자료 정리해줘"
- "흡수해줘"
- "위키 만들어줘"
- "KB 업데이트"
- "knowledge base 업데이트"
- collect 완료 후 "위키에 반영해줘", "정리해줘" 등
- /publish-collect 완료 직후 자동 트리거 (사용자가 흡수를 요청한 경우)
```

## 사전 조건

- `config.yaml` 존재 (미존재 시: "먼저 /publish-setup을 실행해 워크스페이스를 초기화하세요.")
- `raw/entries/`에 `absorbed: false` && `deleted: false` 항목이 1건 이상 존재

미흡수 항목이 없으면 사용자에게 알린다:
```
흡수할 항목이 없습니다. raw/entries/의 모든 항목이 이미 처리되었습니다.
새 자료를 수집하려면 /publish-collect를 실행하세요.
```

---

## WHEN TRIGGERED - EXECUTE IMMEDIATELY

### Step 0: 스냅샷 생성 (pre_absorb)

롤백을 위해 흡수 실행 전 스냅샷을 생성한다.

1. 현재 타임스탬프 생성: `YYYYMMDDTHHMMSS` 형식 (예: `20260422T140000`)
2. `snapshots/{timestamp}/` 디렉토리 생성
3. 현재 `wiki/_index.md` → `snapshots/{timestamp}/wiki/_index.md` 복사
4. 현재 `wiki/_backlinks.json` → `snapshots/{timestamp}/wiki/_backlinks.json` 복사
5. `snapshots/{timestamp}/manifest.json` 생성:

```json
{
  "created_at": "{ISO 8601 타임스탬프}",
  "trigger": "pre_absorb",
  "batch_id": "{이번 세션의 batch_id}",
  "article_count": {스냅샷 시점의 기사 수},
  "description": "absorb {N}건 실행 전 스냅샷"
}
```

스냅샷 생성 후 사용자에게 간단히 보고:
```
스냅샷 생성: snapshots/{timestamp}/
```

---

### Step 1: 미흡수 항목 스캔 및 배치 구성

#### 1a: _absorb_log.json 확인 (중단 재개)

`wiki/_absorb_log.json`을 읽어 중단된 배치가 있는지 확인한다:
- `status: "in_progress"` 배치가 존재하면 → `pending_entries` 목록에서 미처리 항목부터 재개
- 중단된 배치 없으면 → 새 배치로 시작

#### 1b: raw/entries/ 스캔

`raw/entries/` 디렉토리의 모든 `.md` 파일을 스캔하여:
- `absorbed: false` 이고 `deleted: false`인 항목만 수집
- `ingested_at` 기준 오름차순 정렬 (오래된 항목 먼저)

수집 결과를 사용자에게 보고:
```
미흡수 항목: {N}건
배치 크기: {batch_size} (config.yaml 기본값: 15)
예상 배치 수: {ceil(N/batch_size)}
```

#### 1c: batch_id 생성

```
batch_{YYYYMMDD}_{순번}
예: batch_20260422_1
```

같은 날 여러 번 실행 시 순번 증가.

#### 1d: _absorb_log.json 초기 업데이트

```json
{
  "last_batch_id": "{batch_id}",
  "last_processed_at": "{시작 시각}",
  "batches": [
    {
      "batch_id": "{batch_id}",
      "started_at": "{시작 시각}",
      "completed_at": null,
      "entries_total": {N},
      "entries_processed": 0,
      "articles_created": 0,
      "articles_updated": 0,
      "status": "in_progress"
    }
  ],
  "pending_entries": ["{entry 파일명 목록}"]
}
```

---

### Step 2: 배치 처리

`batch_size`건씩 반복 처리한다. 각 배치가 끝날 때마다 체크포인트를 기록한다.

#### 2a: 항목 분석 — "이것이 무엇을 의미하는가?"

각 항목에 대해 `publish-absorb/references/absorb-prompt.md`의 항목 분석 프롬프트를 적용한다.

분석 결과로 다음을 결정한다:
1. **핵심 주제** — 파일 제목이 아닌, 이 항목이 담고 있는 실질적 의미
2. **카테고리** — people / concepts / sermons / books / passages / references 중 하나
3. **기사 제목 후보** — 위키에서 사용할 제목

#### 2b: 기존 기사 매칭 (4단계)

`shared/references/absorb-rules.md`의 매칭 로직을 적용한다:

**매칭 4단계 (순서대로):**

1. **제목/주제 매칭** — 해당 카테고리의 `_index.md`를 읽어 기사 제목과 비교. 직접적으로 같은 주제인 기사 탐색.

2. **위키링크 중첩** — 항목에서 추출한 핵심 키워드가 기존 기사의 `tags`/`related` 필드와 겹치는 정도 측정. 중첩이 높은 기사를 후보로 선정.

3. **카테고리 일치** — 동일 카테고리 내 기사 우선 검토. 카테고리가 다르면 매칭 가능성 낮음.

4. **LLM 판단** — 후보 기사 2-3개의 `index.md` 요약을 읽고 최종 결정:
   - **병합(merge)**: 같은 주제의 기존 기사가 있고, 새 내용이 그 기사에 자연스럽게 통합 가능
   - **신규 생성(create)**: 기존 기사가 없거나, 주제가 충분히 독립적

**Anti-cramming 체크:** 매칭된 기존 기사가 200줄 이상이고, 새 내용이 독립 가능한 하위 주제라면 → 병합 대신 신규 기사 생성으로 전환.

**Anti-thinning 체크:** 신규 생성 시 예상 기사 길이가 15줄 미만이라면 → 가장 관련 높은 기존 기사에 짧은 섹션으로 병합.

#### 2c: 기사 생성 또는 병합

`shared/references/wiki-article-format.md`의 2-tier 포맷을 따른다.

**신규 기사 생성:**

```
wiki/{category}/{기사명}/
├── index.md    ← 기사 본문 (요약 필수)
└── chunks/     ← 100줄 이상 시 분리
    ├── 001.md
    └── 002.md  (필요 시)
```

`index.md` 프론트매터:
```yaml
---
title: {기사명}
type: {카테고리 단수형: person|concept|sermon|book|passage|reference}
created: {오늘 날짜}
updated: {오늘 날짜}
summary: "{저자의 입장 또는 항목 핵심을 2-3문장으로 — LLM 검색 시 이 필드가 핵심}"
related:
  - "[[관련기사1]]"
  - "[[관련기사2]]"
sources:
  - {source_id}
tags:
  - {관련 태그}
chunk_count: {청크 수, 없으면 0}
---
```

기사 본문 작성 규칙:
- `absorb-prompt.md`의 기사 작성 지침 준수
- 백과사전식, 중립적 어조
- 상단 요약 블록 필수: `> **요약:** {2-3문장}`
- 본문에 관련 개념 위키링크 적용: `[[구원론]]`, `[[칭의]]` 등

**기존 기사 병합:**

1. 기존 `wiki/{category}/{기사명}/index.md` 전문 읽기
2. 기존 `chunks/` 파일들 읽기 (있는 경우)
3. `absorb-prompt.md`의 병합 프롬프트 적용:
   - 기존 내용을 완전히 재독 후 새 내용과 통합
   - 중복 없이, 흐름 자연스럽게 재구성
   - 새 출처를 `sources` 배열에 추가
   - `updated` 날짜 갱신
   - 200줄 초과 시 chunks/ 분리 재검토

#### 2d: 개념 기사 자동 생성/갱신

흡수 중 반복적으로 등장하는 신학 개념을 감지하면 `wiki/concepts/`에 자동으로 개념 기사를 생성하거나 갱신한다.

판단 기준:
- 같은 개념 키워드가 2건 이상의 항목에 등장
- 해당 개념에 대한 저자의 고유한 입장이나 정의가 포함된 경우

개념 기사 형식: 일반 기사와 동일 (2-tier), `type: concept`.

#### 2e: 위키링크 및 역링크 업데이트

각 기사 작성/갱신 후:

1. **위키링크 추출** — 기사 본문에서 `[[기사명]]` 패턴 모두 추출
2. **_backlinks.json 갱신** — 추출된 링크 대상 기사에 현재 기사명을 역링크로 추가:
   ```json
   {
     "구원론": ["은혜", "칭의", "로마서_강해_3"],
     "은혜": ["구원론", "2024_부활절_설교"]
   }
   ```
3. **관련 기사 related 필드 상호 업데이트** — 링크된 기사의 `related` 배열에도 현재 기사 추가 (아직 없는 경우)

#### 2f: 체크포인트 기록

각 항목 처리 완료 후:

1. 해당 `raw/entries/{파일명}.md`의 프론트매터에서 `absorbed: true` 로 업데이트
2. `_absorb_log.json` 갱신:
   - `entries_processed` 카운트 증가
   - `pending_entries`에서 해당 항목 제거
   - `articles_created` / `articles_updated` 카운트 갱신
3. 배치 전체 완료 시 `status: "completed"`, `completed_at` 기록

중단 후 재개 시: `pending_entries`에 남은 항목부터 이어서 처리. 이미 `absorbed: true`인 항목은 자동으로 건너뜀.

---

### Step 3: 인덱스 재구축

모든 배치 처리 완료 후 인덱스를 전면 재구축한다.

#### 3a: 카테고리별 _index.md 재생성

각 카테고리 (`people`, `concepts`, `sermons`, `books`, `passages`, `references`)의 `_index.md`를 해당 카테고리 내 모든 기사 목록으로 재생성:

```markdown
# {Category} Index

- [[기사명1]] — {summary 한줄 요약}
- [[기사명2]] — {summary 한줄 요약}
```

기사명 가나다/알파벳순 정렬.

#### 3b: 루트 wiki/_index.md 재생성

전체 KB의 마스터 인덱스:

```markdown
# Wiki Index

총 {N}개 기사 | 마지막 갱신: {날짜}

## People
- [[기사명]] — {summary}

## Concepts
- [[기사명]] — {summary}

## Sermons
...

## Books
...

## Passages
...

## References
...
```

#### 3c: _backlinks.json 최종 정리

전체 `wiki/` 디렉토리를 재스캔하여 `_backlinks.json`을 완전히 재구축한다. 삭제된 기사에 대한 역링크 참조를 정리.

---

### Step 4: 흡수 리포트

사용자에게 최종 결과를 보고한다:

```
흡수 완료

처리: {N}건
  신규 기사: {M}개
  갱신 기사: {K}개
  개념 기사 자동 생성: {J}개

새로 추가된 개념:
  - [[개념1]] — {한줄 설명}
  - [[개념2]] — {한줄 설명}

위키 현황:
  전체 기사: {총 수}개
  스냅샷: snapshots/{timestamp}/

다음 단계:
  - 저자 프로필을 분석하려면: /publish-profile
  - 집필을 시작하려면: /publish-write
  - 위키를 검수하려면: /publish-curate
```

---

## 품질 기준

### Anti-cramming (과밀 방지)

기존 기사에 무분별하게 내용을 추가하지 않는다.

- 기존 기사가 **200줄 이상**이고, 새 내용이 독립적인 하위 주제로 성장 가능한 경우 → 별도 기사로 분리
- 예: `구원론` 기사가 방대해지면 → `칭의`, `성화`, `예정론` 등 별도 기사로 분리 후 `구원론`에서 위키링크로 연결

### Anti-thinning (과소 방지)

너무 작은 스텁(stub) 기사를 만들지 않는다.

- 예상 기사 길이가 **15줄 미만**이면 → 가장 관련 높은 기존 기사의 섹션으로 병합
- 예외: 인명 기사(people)는 15줄 미만이어도 독립 기사로 허용

### 기사 어조

- **백과사전식, 중립적** — LLM Wiki 방식을 따른다
- 1차 자료(저자 본인 글): "저자는 ~라고 주장한다", "저자의 입장은 ~이다"
- 2차 자료(참고문헌): "~에 따르면", "~는 ~라고 설명한다"
- 감정적 표현, 과장 금지

---

## 참조 문서

- `shared/references/workspace-schema.md` — 워크스페이스 구조 + 전체 스키마
- `shared/references/wiki-article-format.md` — 2-tier 기사 포맷 + 위키링크 규칙
- `shared/references/absorb-rules.md` — 흡수 매칭/분리/병합 로직 상세
- `shared/references/search-strategy.md` — 계층적 요약 검색 전략
- `publish-absorb/references/absorb-prompt.md` — 흡수용 LLM 프롬프트 템플릿
