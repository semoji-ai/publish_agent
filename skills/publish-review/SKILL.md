---
name: publish-review
description: Use when users say "/publish-review", "검토해줘", "교정해줘", "심사해줘", "고쳐줘", "퇴고해줘", or after a draft is completed and needs review against the author's KB and profile
---

# Publish Review — 초안 심사 및 교정

KB(wiki/)와 저자 프로필(authors/)을 기준으로 초안을 심사하고 교정한다.

> **핵심 원칙:** 신학적 검증은 "절대적 정답"이 기준이 아니다. **해당 저자의 신학적 입장(theology.yaml)과의 일관성**이 유일한 기준이다. 각 목사님의 신학적 관점 차이는 존중된다.

## 트리거 조건

```
- "/publish-review"
- "/publish-review [파일명]"        # 특정 파일 지정
- "검토해줘"
- "교정해줘"
- "심사해줘"
- "고쳐줘"
- "퇴고해줘"
- "초안 확인해줘"
- "이 글 봐줘"
- "review this draft"
- "proofread this"
- /publish-write 완료 후 자동 연계 시
```

## 사전 조건

1. `config.yaml` 존재 (워크스페이스 초기화 완료)
2. `authors/{author_id}/` — 저자 프로필 4파일 존재 (theology.yaml, style.yaml, sermon_pattern.yaml, vocabulary.md)
3. `projects/{project_name}/drafts/` — 심사할 초안 파일이 1개 이상 존재

사전 조건 미충족 시:
- config.yaml 없음 → "/publish-setup을 먼저 실행해주세요."
- 저자 프로필 미완성 → "/publish-profile을 먼저 실행하여 저자 프로필을 구축해주세요."
- drafts/ 비어 있음 → "심사할 초안이 없습니다. /publish-write로 초안을 먼저 작성해주세요."

---

## WHEN TRIGGERED - EXECUTE IMMEDIATELY

### Step 1: 심사 대상 확인

config.yaml에서 워크스페이스 경로와 author_id를 로드한다.

심사 대상을 결정한다:
- 사용자가 특정 파일을 지정한 경우 → 해당 파일만 심사
- 파일 미지정 → `projects/` 하위의 모든 `drafts/` 디렉토리를 스캔하여 심사 대상 파일 목록 제시 → 사용자가 선택

심사에서 제외되는 파일:
- 프론트매터에 `deleted: true`인 파일 (soft delete 상태)
- 프론트매터에 `status: done`인 파일 (이미 완료된 항목)

> **Soft delete 정의:** 프론트매터에 `deleted: true` 플래그가 설정된 상태. 파일은 디스크에 유지되나 `_index.md`에서 제외되고, 심사·검색·absorb 대상에서 완전히 제외된다. `/publish-curate`에서 `deleted: false`로 복구 가능.

### Step 1.5: 대용량 초안 분할 심사 판단

심사 대상 파일의 줄 수를 확인한다:

```
500줄 이하 → 단일 심사 (기존 흐름)
500줄 초과 → 섹션 단위 분할 심사:
  1. 파일의 헤딩 구조 또는 챕터 구분점 파악 (Read로 전체 구조만 스캔)
  2. 섹션별로 독립적으로 심사 진행
  3. 각 섹션 심사 완료 후 결과를 파일에 기록 (컨텍스트에 누적하지 않음)
  4. 모든 섹션 완료 후 종합 판정 생성
```

분할 심사 시 각 섹션마다:
- 프로필(style.yaml + theology.yaml) + 관련 wiki + 해당 섹션 텍스트만 컨텍스트에 로드
- 섹션 심사 결과를 `reviews/{YYYYMMDD}_review_r{N}_section_{M}.md`에 저장
- 해당 섹션 원문은 컨텍스트에서 제거 후 다음 섹션으로 이동
- 토큰 예산: 섹션당 읽기 40K + 처리 30K + 출력 20K = 90K

→ 상세 규칙: `shared/references/context-management.md`의 "review 단계 컨텍스트 관리" 섹션 참조

### Step 2: 저자 프로필 전체 로드

`authors/{author_id}/`의 4개 파일을 모두 읽는다:

1. `theology.yaml` — 신학적 입장 (심사 기준: 저자의 관점, 절대적 정답 아님)
2. `style.yaml` — 문체 프로필 (어투, 문장 구조, 수사법)
3. `sermon_pattern.yaml` — 설교 구조 패턴
4. `vocabulary.md` — 자주 쓰는/피하는 표현, 성경 인용 방식

프로필이 비어 있거나 미완성인 경우 사용자에게 알리고 `/publish-profile` 실행을 권고한다. 사용자가 진행을 선택하면 가용한 프로필로 심사를 계속한다.

### Step 3: 관련 wiki/ 기사 로드 (KB 기반 심사)

초안의 주제와 관련된 위키 기사를 계층적으로 탐색한다:

```
Level 0: wiki/_index.md 또는 카테고리별 _index.md 스캔
  → 초안의 주제 키워드와 관련된 기사 후보 선정

Level 1: 후보 기사의 index.md summary 필드 확인
  → 관련성 높은 기사 확정

Level 2: 확정된 기사의 chunks/ 로드
  → 상세 내용 참조 (필요한 것만)
```

검색 방향:
- 신학적 주제 → `wiki/concepts/` 우선
- 특정 설교/본문 → `wiki/sermons/` 또는 `wiki/passages/`
- 저자 저서 참조 → `wiki/books/`

KB 기사는 심사 시 "저자가 이 주제에 대해 이전에 어떻게 다루었는가"를 확인하는 데 사용한다.

### Step 4: 4차원 심사

`publish-review/references/review-rubric.md`의 기준에 따라 4개 차원에서 심사한다.

#### 차원 1: 문체 일관성 (Style Consistency)
- 기준: `style.yaml` + `vocabulary.md`
- 확인 항목: 어투, 문장 길이, 수사법, 자주 쓰는/피하는 표현 사용 여부, 성경 인용 방식

#### 차원 2: 신학적 일관성 (Theological Consistency)
- 기준: `theology.yaml` — **저자의 신학적 입장이 기준, 절대적 정답 아님**
- 확인 항목: 구원론·종말론·교회론 등 핵심 입장과의 일치 여부
- 이전 저술(wiki/ 기사)과의 신학적 연속성 확인
- 타 신학자·교단 견해가 인용되는 경우, 저자의 입장과 명확히 구분되는지 확인

#### 차원 3: 논리 구조 / 설득력
- 확인 항목: 논증 흐름의 명확성, 전제-논거-결론 구조, 독자 적합성
- 설교집/강해서인 경우 `sermon_pattern.yaml`의 구조 패턴과의 일치 여부 추가 확인

#### 차원 4: 문법 / 맞춤법 / 가독성
- 확인 항목: 맞춤법, 띄어쓰기, 문장 호응, 단락 구성의 자연스러움

### Step 5: 심사 리포트 생성

심사 결과를 `projects/{project_name}/reviews/{YYYYMMDD}_review.md`에 저장한다.

리포트 포맷은 `publish-review/references/review-rubric.md`의 리포트 템플릿을 따른다:
- 각 차원별 등급(A/B/C/D)과 구체적 근거
- 이슈별 위치 인용 (파일명 + 문장/단락)
- 구체적 수정 제안
- 종합 판정 (PASS / CONDITIONAL / REVISE)

심사 라운드 번호를 리포트 파일명에 포함한다:
- 1회차: `{YYYYMMDD}_review_r1.md`
- 2회차: `{YYYYMMDD}_review_r2.md`
- 3회차: `{YYYYMMDD}_review_r3.md`

### Step 6: 사용자 확인 및 수정사항 선택

심사 리포트를 사용자에게 제시한다:

```
심사 완료 — 종합 판정: {PASS / CONDITIONAL / REVISE}

차원별 등급:
  문체 일관성:   {A/B/C/D}
  신학적 일관성: {A/B/C/D}
  논리 구조:     {A/B/C/D}
  문법/가독성:   {A/B/C/D}

발견된 이슈 {N}건:
  [이슈 목록 요약]

어떤 수정사항을 반영할까요?
  1. 모두 반영
  2. 선택 반영 (번호 입력)
  3. 없음 (심사만 확인)
```

사용자의 선택에 따라 승인된 수정사항만 초안 파일에 반영한다.

수정 시 원본을 덮어쓰기 전에 백업하지 않는다 (프로젝트 디렉토리 자체가 버전 관리 기준). 단, 사용자가 명시적으로 원본 유지를 원하면 `drafts/{filename}_original.md`로 사본 보존 후 수정본 저장.

### Step 7: 재심사 루프

수정사항 반영 후 다음을 사용자에게 묻는다:

```
수정사항이 반영되었습니다.
재심사를 진행할까요? (최대 {review_max_rounds}회 중 {N}회차 완료)
```

- 사용자 승인 시 → Step 3부터 반복 (이번 라운드 리포트 파일명에 회차 번호 갱신)
- 사용자 거부 시 → 심사 종료, 최종 상태 보고

**최대 횟수 도달 시 처리:**
- `config.yaml`의 `defaults.review_max_rounds` 값 사용 (기본값: 3)
- 최대 횟수에 도달했는데 미해결 이슈(C 또는 D 등급 항목)가 남아 있으면:

```
최대 심사 횟수({review_max_rounds}회)에 도달했습니다.
아직 해결되지 않은 이슈가 {N}건 남아 있습니다.

미해결 이슈:
  [목록]

이 항목들은 저자님의 직접 판단이 필요합니다.
reviews/{YYYYMMDD}_review_r{N}_unresolved.md에 미해결 이슈 목록을 저장했습니다.
```

미해결 이슈 목록을 별도 파일에 저장하고 심사를 종료한다.

---

## 커스텀 심사 기준

`publish-review/references/custom-rubric.md` 파일이 존재하면 **공통 rubric보다 우선 적용**한다.
없으면 `review-rubric.md`를 기본으로 사용한다.

커스텀 rubric에는 특정 사용자/교회에 맞는 심사 기준을 정의할 수 있다:
- 특정 차원의 가중치 조정 (예: "적용" 비중 강화)
- 추가 심사 차원 (예: "교회 비전과의 정합성")
- 등급 기준 변경

## 참조 문서

- `shared/references/author-profile-schema.md` — 저자 프로필 4파일 스키마
- `shared/references/search-strategy.md` — wiki/ 계층적 검색 전략
- `shared/references/workspace-schema.md` — 워크스페이스 구조 + 스키마
- `shared/references/context-management.md` — 컨텍스트 윈도우 관리 전략 + 섹션 분할 심사 규칙
- `publish-review/references/review-rubric.md` — 4차원 심사 기준표 (공통)
- `publish-review/references/custom-rubric.md` — 사용자별 심사 기준 (있으면 우선 적용)
