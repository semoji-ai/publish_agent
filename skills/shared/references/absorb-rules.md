---
name: absorb-rules
description: Publish Agent 흡수(absorption) 로직의 상세 규칙. 기존 기사 매칭 4단계, Anti-cramming/Anti-thinning 기준, 카테고리 결정, 배치 처리, 스냅샷 자동 생성, 인덱스 재구축 규칙.
---

# 흡수 규칙 (Absorb Rules)

`/publish-absorb` 스킬이 raw entry를 위키 기사로 변환할 때 따르는 규칙의 완전한 명세. LLM이 이 문서를 참조하여 흡수 결정을 내린다.

---

## 1. 흡수 전 준비

### 1.1 스냅샷 자동 생성

absorb 실행 시작 전 **반드시** 스냅샷을 생성한다.

```
snapshots/{YYYY-MM-DDTHHMMSS}/
├── manifest.json
├── wiki/_index.md
└── wiki/_backlinks.json
```

`manifest.json` 내용:
```json
{
  "created_at": "{timestamp}",
  "trigger": "pre_absorb",
  "batch_id": "{현재 배치 ID}",
  "article_count": {현재 전체 기사 수},
  "description": "absorb {N}건 실행 전 스냅샷"
}
```

**스냅샷 없이 absorb 진행 금지.** 스냅샷 생성 실패 시 사용자에게 알리고 중단.

### 1.2 미흡수 항목 스캔

`raw/entries/` 디렉토리에서 다음 조건을 모두 만족하는 파일을 대상으로 선정:
- `absorbed: false`
- `deleted: false`

`_absorb_log.json`의 `pending_entries` 확인:
- `status: "in_progress"`인 배치가 있으면 해당 배치의 `pending_entries`부터 시작 (재개 모드)
- 없으면 신규 배치 시작

### 1.3 배치 구성

- 배치 크기: `config.yaml`의 `defaults.batch_size` (기본값: 15)
- 배치 ID: `batch_{YYYYMMDD}` (당일 복수 배치 시 `batch_{YYYYMMDD}_2`, `_3` 등)
- `_absorb_log.json` 업데이트:

```json
{
  "batch_id": "batch_20260422",
  "started_at": "{ISO 8601}",
  "completed_at": null,
  "entries_total": {총 미흡수 항목 수},
  "entries_processed": 0,
  "articles_created": 0,
  "articles_updated": 0,
  "status": "in_progress"
}
```

---

## 2. 기존 기사 매칭 4단계

각 raw entry에 대해 다음 4단계 순서로 기존 위키 기사와의 매칭을 판단한다.

### Step 1: 제목/주제 매칭

**방법:**
1. raw entry의 YAML 프론트매터 `title` 필드 확인
2. 본문 첫 문단에서 핵심 주제어 3-5개 추출
3. `wiki/_index.md` 또는 해당 카테고리 `_index.md` 스캔

**매칭 판단:**
- raw entry 제목 또는 핵심 주제어가 기존 기사 제목과 **정확히 일치** → 강력한 매칭 후보
- 유사 표현(동의어, 축약형) 일치 → 약한 매칭 후보

**예시:**
- raw entry: `title: "칭의 교리"` → `wiki/concepts/칭의/` 기사와 매칭 검토
- raw entry: `title: "2024년 부활절 설교"` → `wiki/sermons/2024_부활절_설교/` 기사와 매칭 검토

### Step 2: 위키링크/태그 중첩 분석

**방법:**
1. raw entry 본문에서 잠재적 위키링크 키워드 추출 (주요 명사, 고유명사)
2. 기존 기사들의 `related` 필드와 `tags` 필드와 중첩 정도 계산

**매칭 점수 기준:**
- 중첩 키워드 3개 이상: 강한 관련성
- 중첩 키워드 1-2개: 약한 관련성
- 중첩 없음: 관련성 없음

**활용 방법:**
- Step 1에서 후보가 나왔다면 이 단계로 후보의 신뢰도 확인
- Step 1에서 후보가 없었다면 이 단계로 잠재 후보 추가 발굴

### Step 3: 카테고리 일치 확인

raw entry의 `category` 필드를 기준으로 검색 범위를 좁힌다.

| raw entry category | 우선 탐색 카테고리 | 보조 탐색 카테고리 |
|-------------------|-----------------|-----------------|
| `sermon` | `wiki/sermons/` | `wiki/concepts/`, `wiki/passages/` |
| `book` | `wiki/books/` | `wiki/concepts/` |
| `essay` | `wiki/concepts/` | `wiki/books/` |
| `commentary` | `wiki/passages/`, `wiki/references/` | `wiki/concepts/` |
| `thesis` | `wiki/references/` | `wiki/concepts/` |
| `article` | `wiki/references/` | `wiki/concepts/` |

**규칙:** 같은 카테고리 내 기사를 우선 검토. 카테고리 간 병합은 Step 4(LLM 판단)에서만 결정.

### Step 4: LLM 최종 판단

앞 3단계로 후보가 특정되면, LLM이 다음을 결정한다:

#### 판단 옵션 A: 기존 기사에 병합(merge)

조건:
- 명확한 매칭 후보가 있고
- 새 내용이 기존 기사의 주제 범위 내에 있으며
- Anti-cramming 기준(아래 3장)을 위반하지 않음

작업:
1. 기존 기사 `index.md` 재읽기
2. 새 내용을 적절한 섹션에 통합
3. `summary` 업데이트 (필요한 경우)
4. `sources` 배열에 새 source_id 추가
5. `updated` 날짜 갱신
6. chunks/ 업데이트 (내용이 추가된 경우)

#### 판단 옵션 B: 신규 기사 생성(create)

조건:
- 매칭 후보가 없거나 불명확
- 새 내용이 기존 기사와 독립적인 주제
- Anti-thinning 기준(아래 4장)을 통과함 (최소 15줄 이상의 독립적 내용)

작업:
1. 적절한 카테고리 결정 (아래 5장)
2. `{article_name}` 결정 (제목 기반, 옵시디언 호환)
3. `wiki/{category}/{article_name}/index.md` 생성
4. 필요 시 `chunks/` 생성

#### 판단 옵션 C: 분리(split) — 기존 기사에서 일부 추출

조건: Anti-cramming 기준 위반 시 (아래 3장)

---

## 3. Anti-cramming 규칙 (과밀 방지)

### 분리 트리거

다음 **두 조건 모두** 충족 시 기존 기사에 병합하지 않고 별도 기사로 분리:

1. 기존 기사(index.md + 모든 chunks/*.md)의 **총 줄 수 ≥ 200줄**
2. 새 내용(또는 기존 기사 내 특정 섹션)이 **독립 기사로 성장 가능** — 즉, 최소 15줄 이상의 독자적인 논점/사례를 가짐

### 분리 판단 예시

| 상황 | 판단 |
|------|------|
| `구원론` 기사 250줄 + 새 `칭의` 관련 내용 30줄 추가 시도 | **분리** → `칭의` 별도 기사 생성 |
| `구원론` 기사 180줄 + 새 내용 20줄 추가 시도 | **병합** (분량 기준 미달) |
| `구원론` 기사 220줄 + 새 내용 10줄 추가 시도 | **병합** (새 내용 독립 불가) |
| `구원론` 기사 220줄에서 기존 `칭의` 섹션이 이미 80줄 | **분리 검토** → `칭의` 섹션을 별도 기사로 추출 권장 |

### 분리 절차

1. 새 기사로 분리할 내용의 범위 결정
2. 새 `{article_name}` 결정
3. 새 기사 `index.md` 생성 (기존 기사의 해당 섹션 내용 기반)
4. 기존 기사에서 해당 섹션 내용을 요약으로 대체 + 새 기사로의 위키링크 추가
5. 양쪽 기사의 `related` 필드 상호 업데이트
6. `_backlinks.json` 갱신

### 줄 수 계산 기준

- YAML 프론트매터 제외
- 빈 줄 포함
- 모든 chunks/*.md 파일 합산 포함
- `index.md` + `chunks/001.md` + `chunks/002.md` = 전체 기사 분량

---

## 4. Anti-thinning 규칙 (과소 방지)

### 병합 트리거

새 기사 생성 시 독립된 내용이 **15줄 미만**이면 새 기사로 생성하지 말고 관련 기사에 병합.

### 병합 대상 선택 순서

1. Step 1-3에서 발견된 가장 연관성 높은 기존 기사
2. 없으면, raw entry의 상위 개념에 해당하는 기존 기사에 새 섹션 추가
3. 상위 개념 기사도 없으면, 예외적으로 신규 생성 허용 (단, 향후 보완 표시)

### 예외 허용 (15줄 미만이어도 신규 생성 가능)

- **고유명사 스텁**: 인물(`people/`), 특정 설교(`sermons/`), 특정 저서(`books/`) — 추후 내용 추가를 위해 스텁 허용
- **교차 참조 허브**: 여러 기존 기사에서 이미 `[[링크]]`로 참조되고 있는 개념

### 적용 예시

| 상황 | 판단 |
|------|------|
| `루터의 칭의론`에 대한 8줄 내용 (참고자료) | **병합** → 기존 `칭의` 기사에 섹션 추가 |
| `칼빈` 인물 정보 5줄 | **신규 생성 허용** (고유명사 스텁) |
| `성화` 개념 12줄 (여러 기사에서 이미 `[[성화]]`로 링크됨) | **신규 생성 허용** (교차 참조 허브) |

---

## 5. 카테고리 결정 기준

새 기사를 생성할 때 `wiki/` 하위 카테고리를 결정하는 규칙.

| 카테고리 | 해당하는 내용 | 기사명 형식 예시 |
|----------|-------------|----------------|
| `people/` | 신학자, 성경 인물, 저자, 역사적 인물 | `칼빈`, `바울`, `어거스틴` |
| `concepts/` | 신학 교리, 개념, 주제 | `구원론`, `칭의`, `은혜`, `언약` |
| `sermons/` | 개별 설교 기록 및 분석 | `2024_부활절_설교`, `2023_로마서_강해_3` |
| `books/` | 저자의 저서 또는 참고 도서 전체 | `믿음의_여정`, `기독교강요` |
| `passages/` | 성경 특정 본문/단락에 대한 기사 | `로마서_8장`, `요한복음_3:16` |
| `references/` | 논문, 주석서, 외부 참고자료 | `웨스트민스터신앙고백_해설`, `BDAG_은혜` |

### 경계 사례 처리

- **설교에서 추출된 신학 개념**: `concepts/`에 신규 기사 + `sermons/` 기사에서 위키링크
- **저서의 특정 장**: `books/` 기사(저서 전체) + 필요 시 `concepts/` 기사(해당 장의 주제)
- **성경 인물**: `people/` (신학적 인물로서) + 필요 시 `passages/` (해당 인물이 등장하는 본문)

---

## 6. 배치 처리 및 체크포인트

### 배치 단위 처리 흐름

```
배치 시작
  ↓
항목 1 처리 → absorbed: true 마킹 → _absorb_log.json 업데이트
  ↓
항목 2 처리 → absorbed: true 마킹 → _absorb_log.json 업데이트
  ↓
...
  ↓
항목 N (batch_size) 처리 완료
  ↓
배치 완료: status → "completed", completed_at 기록
```

### 체크포인트 저장 규칙

**각 항목 처리 완료마다** 즉시:
1. 해당 raw entry의 `absorbed: true` 마킹
2. `_absorb_log.json`의 `entries_processed` 카운트 증가
3. `_absorb_log.json`의 `pending_entries`에서 해당 파일명 제거
4. `articles_created` 또는 `articles_updated` 카운트 증가

**이유:** 체크포인트를 자주 저장하면 중단 시 재개 가능 범위를 최소화한다.

### 중단 재개 (Resume) 로직

absorb 시작 시:

```
1. _absorb_log.json 읽기
2. status: "in_progress"인 배치 존재?
   → YES: 해당 배치의 pending_entries 목록 로드
          pending_entries[0]부터 이어서 처리
   → NO:  신규 배치 생성, absorbed: false 항목 전체 스캔
3. 이미 absorbed: true인 항목은 건너뜀 (중복 처리 방지)
```

### 배치 크기 조정 가이드

| 상황 | 권장 batch_size |
|------|---------------|
| 기본값 | 15 |
| 컨텍스트 창이 작은 플랫폼 | 5-10 |
| 기사가 매우 길고 복잡한 경우 | 5-8 |
| 단순한 설교 텍스트 대량 처리 | 20-30 |

---

## 7. _index.md 재구축 규칙

### 재구축 시점

1. **배치 처리 완료 후** (전체 absorb 완료 시)
2. curate에서 기사 삭제/복구 후
3. 사용자 명시적 요청 시

### 재구축 절차

#### 카테고리별 _index.md 재구축

각 카테고리 디렉토리(`wiki/concepts/` 등)에 대해:

1. 해당 카테고리 내 모든 `index.md` 파일 스캔
2. `deleted: true` 기사 제외
3. 각 기사의 `title`과 `summary`(첫 문장) 추출
4. 가나다/알파벳 순 정렬
5. 카테고리 `_index.md` 생성:

```markdown
# {Category} Index

- [[{title}]] — {summary 첫 문장 또는 압축}
- [[{title}]] — {summary 첫 문장 또는 압축}
...
```

#### 루트 _index.md 재구축

`wiki/_index.md`:

```markdown
# Wiki Index

> 총 {N}개 기사 | 마지막 업데이트: {date}

## Concepts ({n}개)
{카테고리 내 기사 목록}

## People ({n}개)
...

## Sermons ({n}개)
...

## Books ({n}개)
...

## Passages ({n}개)
...

## References ({n}개)
...
```

#### _backlinks.json 재구축

1. wiki/ 하위 모든 `index.md` 스캔
2. `deleted: true` 기사 제외
3. 각 파일에서 `[[기사명]]` 패턴 추출
4. 역링크 관계 구성 (`기사B`에서 `[[기사A]]`를 링크하면 → `기사A`의 역링크 배열에 `기사B` 추가)
5. `_backlinks.json` 전체 덮어쓰기

---

## 8. 개념 기사 자동 생성 패턴

absorb 중 raw entry 분석 시, 다음 기준으로 `concepts/` 카테고리에 개념 기사를 자동 생성/갱신한다:

### 트리거 조건

raw entry 분석에서 다음 중 하나 해당 시:
1. 여러 기사에서 반복 등장하는 신학 개념 (3회 이상 `[[링크]]` 참조)
2. raw entry의 핵심 주제가 단일 개념 기사로 정리될 수 있는 경우
3. 기존 기사에서 섹션이 Anti-cramming 기준으로 분리되어 새 concepts/ 기사가 필요한 경우

### 자동 생성 시 작성 톤

- 저자의 1차 자료 기반: "저자는 ~라고 주장한다", "저자의 입장은 ~이다"
- 참고 자료 기반: "~에 따르면", "~는 ~로 정의한다"
- 백과사전식, 중립적 기술
- 개인 의견이나 LLM의 평가 포함 금지

---

## 9. 흡수 완료 처리

배치 완료 후:

1. `_absorb_log.json` 업데이트: `status: "completed"`, `completed_at` 기록
2. `wiki/_index.md` 재구축
3. 각 카테고리 `_index.md` 재구축
4. `_backlinks.json` 재구축
5. 흡수 리포트 생성:
   - 처리한 항목 수
   - 생성된 기사 수 + 기사 이름 목록
   - 갱신된 기사 수 + 기사 이름 목록
   - 새로 발견된 개념 기사 목록
   - 다음 단계 제안 ("저자 프로필을 업데이트하시겠습니까?")
