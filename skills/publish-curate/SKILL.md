---
name: publish-curate
description: Use when users say "/publish-curate", "위키 정리해줘", "잘못된 자료 확인", "배치 롤백", or want to clean up or fix the knowledge base
---

# Publish Curate — KB 검수 및 정리

저자 프로필 기준으로 위키(KB)를 스캔하여 이질적인 항목을 감지하고, soft delete 또는 스냅샷 롤백으로 제거한다. 모든 삭제는 복구 가능하다.

## 트리거 조건

```
- "/publish-curate"
- "위키 정리해줘"
- "잘못된 자료 있는지 확인해줘"
- "오염된 자료 찾아줘"
- "이 배치 롤백해줘"
- "배치 롤백"
- "KB 정리"
- "knowledge base 정리해줘"
```

## 사전 조건

- config.yaml 존재 (publish-setup 완료)
- wiki/ 디렉토리에 기사 존재
- authors/{author_id}/ 프로필 파일 존재 (publish-profile 실행 권장)

---

## WHEN TRIGGERED - EXECUTE IMMEDIATELY

### Step 1: 검수 범위 확인

사용자에게 검수 범위를 확인한다:

```
1. 전체 — wiki/ 모든 기사 대상
2. 특정 배치 — batch_id 지정 (예: batch_20260421)
3. 특정 출처 — source_id 지정 (예: src_20260421_003)
```

범위가 명확하지 않으면 질문한다. 단, 사용자가 "이 배치 롤백해줘"처럼 의도가 명확하면 추가 질문 없이 진행한다.

**batch_id / source_id 확인 방법:**
- `wiki/_absorb_log.json` 의 `batches` 배열에서 확인
- raw/entries/ 프론트매터의 `batch_id`, `source_id` 필드에서 확인

### Step 2: 자동 스냅샷 생성

검수 실행 전 반드시 스냅샷을 생성한다. 롤백 기준점이 된다.

생성 위치: `snapshots/{YYYY-MM-DDTHHMMSS}/`

생성 파일:
1. `manifest.json`
   ```json
   {
     "created_at": "{ISO 8601 타임스탬프}",
     "trigger": "pre_curate",
     "description": "curate 실행 전 자동 스냅샷",
     "article_count": {현재 wiki/ 기사 수}
   }
   ```
2. `wiki/_index.md` 사본
3. `wiki/_backlinks.json` 사본

### Step 3: 저자 프로필 로드

`config.yaml`에서 `author.id`를 읽어 `authors/{author_id}/` 하위 4개 파일을 로드한다:

- `theology.yaml` — 신학적 입장
- `style.yaml` — 문체
- `sermon_pattern.yaml` — 설교 구조 패턴
- `vocabulary.md` — 어휘 패턴

프로필이 비어 있으면 (publish-profile 미실행 상태) 경고를 표시하고 계속 진행한다:
```
저자 프로필이 비어 있습니다. /publish-profile을 먼저 실행하면 더 정확한 이질성 감지가 가능합니다.
현재 상태로 진행하려면 엔터를 누르세요.
```

### Step 4: 대상 항목 스캔 및 이질성 감지

검수 범위에 해당하는 기사/항목을 스캔한다. `deleted: true`인 항목은 건너뛴다.

**스캔 대상:**
- 범위 = 전체: `wiki/` 모든 카테고리의 `index.md`
- 범위 = 특정 배치: 해당 `batch_id`가 `sources` 필드에 포함된 기사
- 범위 = 특정 출처: 해당 `source_id`가 `sources` 필드에 포함된 기사

**이질성 감지 기준 (저자 프로필 대비):**

| 유형 | 감지 조건 | 심각도 |
|------|-----------|--------|
| 신학적 이질성 | 기사 내용이 theology.yaml의 저자 입장과 상충 | HIGH |
| 문체 불일치 | 저자 1차 자료(primary)인데 style.yaml과 현저히 다른 어투 | MEDIUM |
| 출처 혼용 | reference 자료가 저자의 주장으로 표현됨 | HIGH |
| 카테고리 오분류 | 설교가 concepts/에 들어간 경우 등 | LOW |
| 중복 의심 | 동일 내용이 복수 기사에 분산 | LOW |

각 항목에 대해 이질성 여부와 유형을 판단한다. 이질성이 없는 항목은 리포트에서 제외한다.

### Step 5: 플래그 리포트 출력

이질성이 감지된 항목을 표 형태로 사용자에게 제시한다:

```
## 검수 결과: {N}개 항목 플래그됨

| 기사명 | 이질성 유형 | 출처(source_id) | 배치(batch_id) | 심각도 |
|--------|------------|----------------|----------------|--------|
| 구원론  | 신학적 이질성: 저자 입장(개혁주의)과 상충하는 아르미니우스적 서술 | src_20260421_007 | batch_20260421 | HIGH |
| 성령론  | 출처 혼용: 참고자료 내용이 저자 주장으로 표현됨 | src_20260421_012 | batch_20260421 | HIGH |
| ...    | ...        | ...            | ...            | ...    |

이질성 없음: {M}개 기사 (스캔 완료)
```

플래그된 항목이 없으면:
```
검수 완료. 이질성이 감지된 항목이 없습니다. 위키 상태가 양호합니다.
```
→ Step 7로 건너뛴다.

### Step 6: 사용자 선택 및 실행

사용자에게 처리 방법을 선택하게 한다:

```
각 항목에 대해 처리 방법을 선택하세요:
  [S] Soft delete — 해당 기사를 삭제 표시 (복구 가능)
  [R] 배치 롤백 — 해당 배치 전체를 롤백
  [I] 무시 — 이 항목은 그대로 유지

항목별로 선택하거나, 전체 일괄 처리를 선택할 수 있습니다.
```

**6a: Soft Delete 실행**

선택된 기사의 `index.md` 프론트매터에 `deleted: true`를 추가한다:

```yaml
---
title: 구원론
deleted: true
# ...나머지 필드 유지
---
```

- 파일 자체는 삭제하지 않는다 (복구 가능)
- 이후 `_index.md`에서 해당 항목을 제외한다
- 해당 기사의 `chunks/`는 유지한다

**6b: 배치 롤백 실행**

1. 사용자가 지정한 `batch_id`에 해당하는 스냅샷을 `snapshots/`에서 찾는다
   - 해당 배치의 absorb 직전 스냅샷 (`manifest.json`의 `batch_id` 확인)
   - 스냅샷이 없으면 경고: "해당 배치의 스냅샷이 없습니다. 개별 soft delete를 사용해주세요."
2. 스냅샷의 `wiki/_index.md`와 `wiki/_backlinks.json`을 현재 파일에 복원한다
3. 해당 배치에서 생성/수정된 기사를 특정하여:
   - 해당 배치에서 **신규 생성**된 기사: `deleted: true` 처리
   - 해당 배치에서 **수정**된 기사: 수정 전 상태 복원 (스냅샷 내 사본 기준)
4. 해당 배치의 raw/entries/ 항목을 `absorbed: false`로 되돌린다

**6c: 무시**

아무 처리도 하지 않고 다음 항목으로 넘어간다. 로그에 "사용자가 무시 선택"을 기록한다.

### Step 7: _index.md 및 _backlinks.json 재구축

처리가 완료된 후 인덱스를 재구축한다.

**_index.md 재구축:**
- `wiki/` 전체 기사 스캔
- `deleted: true`인 기사 제외
- 각 기사의 `title`과 `summary` 필드 추출
- 카테고리별 `_index.md` 재생성
- 루트 `wiki/_index.md` 재생성

**_backlinks.json 재구축:**
- `deleted: true`가 아닌 모든 기사의 `[[위키링크]]` 추출
- 역링크 맵 재구성 후 `wiki/_backlinks.json` 갱신

### Step 8: 완료 리포트

```
검수 완료.

처리 결과:
  Soft delete: {N}개 기사
  배치 롤백: {batch_id} ({M}개 기사 영향)
  무시: {K}개 항목

인덱스 재구축 완료:
  _index.md 갱신
  _backlinks.json 갱신

스냅샷: snapshots/{timestamp}/
복구가 필요하면: "이전 상태로 복구해줘" 또는 해당 스냅샷 경로를 알려주세요.
```

---

## 버전 관리 및 복구 안내

- **Soft delete:** `deleted: true` 플래그만 추가, 파일은 보존됨. 복구 시 `deleted: false`로 변경하고 인덱스 재구축.
- **배치 롤백:** `snapshots/{timestamp}/`의 인덱스와 백링크를 복원. 원본 raw/entries/ 항목은 보존됨.
- **스냅샷 자동 생성 시점:** curate 실행 전, absorb 실행 전
- **수동 복구:** 사용자가 "이전으로 되돌려줘"라고 하면 가장 최근 스냅샷으로 복원 제안

---

## 참조 문서

- `shared/references/workspace-schema.md` — 스냅샷 구조, raw entry 스키마
- `shared/references/absorb-rules.md` — 배치 처리 및 absorbed 상태 관리
