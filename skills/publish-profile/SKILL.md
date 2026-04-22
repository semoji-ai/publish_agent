---
name: publish-profile
description: Use when users say "/publish-profile", "내 문체 분석해줘", "프로필 업데이트", "저자 분석", "내 글 스타일 분석", "신학 프로필 만들어줘", or after a large batch of new materials has been absorbed into the knowledge base
---

# Publish Profile — 저자 프로필 분석/갱신

저자의 1차 자료를 분석하여 문체, 신학적 입장, 설교 구조, 어휘 패턴을 추출하고 `authors/{author_id}/` 프로필 파일 4개를 생성하거나 갱신한다.

## 트리거 조건

```
- "/publish-profile"
- "/publish-profile [분석 대상]"
- "내 문체 분석해줘"
- "프로필 업데이트"
- "저자 프로필 만들어줘"
- "내 글 스타일 분석해줘"
- "신학 프로필 만들어줘"
- "설교 패턴 분석해줘"
- "프로필 갱신해줘"
- 대량 자료 흡수(absorb) 완료 후 사용자 요청 시
- 온보딩 4단계 (publish-absorb 완료 후)
```

## 사전 조건

- `config.yaml` 존재 (publish-setup 완료)
- 다음 중 하나 이상:
  - `wiki/` 디렉토리에 위키 기사 존재
  - `raw/entries/`에 `type: primary` 항목 존재
- **최소 5건 이상의 1차 자료(primary)** 확보 — 미만이면 경고 후 사용자 판단에 위임

---

## WHEN TRIGGERED - EXECUTE IMMEDIATELY

### Step 1: config.yaml 로드

`config.yaml`을 읽어 다음을 확인한다:

- `author.id` → 분석 대상 저자 식별
- `author.name` → 리포트에 사용
- 워크스페이스 경로

### Step 2: 분석 소스 결정

사용자 입력에 따라 분석 범위를 결정한다:

- **전체 분석 (기본):** `wiki/` 전체 기사 + `raw/entries/`의 primary 원본
- **특정 자료 지정:** 사용자가 경로나 자료 유형을 지정한 경우 해당 범위만

**샘플링 전략 (컨텍스트 보호 필수):**

모든 1차 자료를 한 번에 읽지 않는다. 다음 샘플링 방식으로 대표 자료만 추출한다:

```
전체 corpus 목록 파악 (raw/entries/ 스캔, 파일명만 — 본문 읽지 않음)
  ↓
샘플 선택:
  - 최근 10편 (ingested_at 기준 최신)
  - 초기 5편 (ingested_at 기준 가장 오래된 것)
  - 무작위 5편 (전체에서 균등 분산)
  = 최대 20편 샘플
  ↓
각 샘플에서 부분 추출 (Read offset/limit 활용):
  - 서론: 처음 50줄
  - 본론 일부: 중간 100줄 (전체 줄 수의 1/3 지점부터)
  - 결론: 마지막 50줄
  = 파일당 최대 200줄 추출
  ↓
총 최대 4000줄 → 슬라이딩 윈도우로 8청크 분할 처리
(청크당 500줄, 처리 후 원문 버리고 요약만 누적)
```

**wiki 기사 샘플링:**
1. `wiki/sermons/_index.md`, `wiki/books/_index.md`, `wiki/concepts/_index.md` 스캔 (Level 0)
2. 각 카테고리별 대표 기사의 summary만 로드 (Level 1, 카테고리당 최대 10건)
3. 기사 전체(chunks/)는 로드하지 않음 — summary가 분석에 충분

**토큰 예산:** 읽기 40K + 처리 30K + 출력 10K = 80K.

→ 상세 규칙: `shared/references/context-management.md`의 "패턴 3: 샘플링" 섹션 참조

**주의:** `type: reference`인 2차 자료는 분석 대상에서 제외한다. 저자 본인의 글(primary)만 분석한다.

### Step 3: 1차 자료 수량 확인

샘플링된 primary 자료가 5건 미만이면:

```
신뢰도 있는 프로필 분석을 위해 최소 5건의 1차 자료(저자 본인의 글)가 필요합니다.
현재 확보된 1차 자료: {N}건

계속 진행하면 분석 신뢰도가 낮을 수 있습니다.
- 계속 진행: "계속"
- 먼저 자료 수집: /publish-collect 실행 권장
```

사용자가 계속을 선택하면 진행하되 리포트에 낮은 신뢰도 경고를 표시한다.

### Step 4: 기존 프로필 확인

`authors/{author_id}/` 디렉토리를 확인한다:

- **기존 프로필 없음:** 신규 생성 모드로 진행 (Step 5 → Step 7)
- **기존 프로필 있음:** 갱신 모드로 진행 (Step 5 → Step 6 → Step 7)

### Step 5: 4차원 병렬 분석

로드된 자료를 기반으로 4개 차원을 분석한다. 각 차원의 상세 기준은 `publish-profile/references/analysis-dimensions.md`를 참조한다.

가능한 경우 병렬로 실행하고, 병렬 미지원 환경에서는 순차 처리한다.

#### 5a: 문체 분석 → style.yaml

분석 항목:
- 어투: 경어/반말/혼합 여부
- 문장 평균 길이 (단어 수 또는 음절 수 기준)
- 수사법: 은유, 직유, 대조, 반복, 열거 등의 사용 빈도와 유형
- 비유 패턴: 자주 사용하는 비유 소재 (자연, 일상, 역사적 사건 등)
- 논증 방식: 연역적/귀납적/예화 중심
- 단락 길이 경향: 짧은 단락 선호 여부

출력 형식:
```yaml
tone: ""
sentence_length: ""
rhetoric:
  metaphor_frequency: ""
  favorite_metaphors: []
  simile_frequency: ""
  contrast_use: ""
  repetition_use: ""
argumentation: ""
paragraph_style: ""
```

#### 5b: 신학적 입장 분석 → theology.yaml

분석 항목: 구원론, 종말론, 교회론, 성령론, 성경관, 예정론, 성례론

각 항목별:
- `position`: 저자가 취하는 신학적 입장
- `emphasis`: 해당 교리에서 특히 강조하는 측면
- `key_texts`: 자주 인용하는 성경 본문

**중요:** 저자의 실제 입장을 있는 그대로 기록한다. LLM이 해당 입장을 평가하거나 판단하지 않는다. 신학적 다양성을 존중한다.

출력 형식:
```yaml
soteriology:
  position: ""
  emphasis: ""
  key_texts: []
eschatology:
  position: ""
  emphasis: ""
ecclesiology:
  position: ""
pneumatology:
  position: ""
scripture_view:
  position: ""
predestination:
  position: ""
sacraments:
  position: ""
```

#### 5c: 설교 구조 분석 → sermon_pattern.yaml

분석 항목:
- 구조 유형: 귀납적/연역적/내러티브/주제별
- 서론-본론-적용 비율 (0.0~1.0, 합계 1.0)
- 예화 빈도와 유형 (개인 경험, 역사적 사례, 문학 인용 등)
- 성경 인용 방식 (직접 인용/의역/비율)
- 청중 호칭 방식 (성도 여러분, 형제자매 등)

출력 형식:
```yaml
structure: ""
intro_ratio: 0.0
body_ratio: 0.0
application_ratio: 0.0
illustration_frequency: ""
illustration_types: []
scripture_citation_style: ""
audience_address: ""
```

#### 5d: 어휘 패턴 분석 → vocabulary.md

분석 항목:
- 자주 쓰는 표현: 빈도 기반으로 상위 표현 추출
- 피하는 표현/단어: 유사 저자와 비교하거나 명시적으로 회피되는 표현
- 성경 번역본: 주로 사용하는 번역 (개역개정, 새번역, NIV 등)
- 인용 표기 형식: 장절 표기 방식 (예: 요 3:16 vs 요한복음 3장 16절)
- 특징적인 전환어/접속어

출력 형식:
```markdown
## 자주 쓰는 표현
- (표현) — 빈도: 높음/보통

## 피하는 표현

## 성경 번역본
- 주 사용:

## 인용 표기 형식
-

## 특징적 전환어
-
```

### Step 6: diff 생성 (기존 프로필 갱신 모드)

기존 프로필이 있을 경우, 분석 결과와 기존 파일을 비교하여 변경점을 추출한다.

사용자에게 다음 형식으로 변경점을 제시한다:

```
프로필 분석이 완료되었습니다. 다음 변경사항이 감지되었습니다:

[style.yaml]
- tone: "경어체" → "경어체 (간헐적 직접 호칭 포함)"
- rhetoric.favorite_metaphors: ["빛과 어둠"] → ["빛과 어둠", "씨앗과 열매", "여정"]

[theology.yaml]
- soteriology.emphasis: "" → "은혜의 무조건성, 하나님의 주권"
- soteriology.key_texts: [] → ["로마서 8:29-30", "에베소서 2:8-9"]

[sermon_pattern.yaml]
- structure: "" → "귀납적"
- illustration_frequency: "" → "본론당 1-2회"

[vocabulary.md]
- 새로 발견된 자주 쓰는 표현: "은혜 가운데", "말씀이 선포될 때"
- 성경 번역본: "개역개정"

이 변경사항을 적용할까요?
- 전체 적용: "적용"
- 항목별 선택: 적용할 항목을 지정해주세요
- 취소: "취소"
```

### Step 7: 신규 프로필 생성 (신규 모드)

기존 프로필이 없을 경우, 분석 결과 전체를 사용자에게 제시한다.

```
저자 프로필 분석이 완료되었습니다. 다음 내용으로 프로필을 생성합니다:

[문체 — style.yaml]
{분석 결과 전체}

[신학적 입장 — theology.yaml]
{분석 결과 전체}

[설교 구조 — sermon_pattern.yaml]
{분석 결과 전체}

[어휘 패턴 — vocabulary.md]
{분석 결과 전체}

분석 근거 자료: {N}건의 1차 자료 (설교 {a}편, 저서 {b}권, 글 {c}편)

이 내용으로 프로필을 저장할까요? 수정이 필요한 부분이 있으면 알려주세요.
- 저장: "확인" 또는 "저장"
- 수정: 수정할 내용을 직접 알려주세요
- 취소: "취소"
```

### Step 8: 사용자 승인 후 저장

**중요:** 사용자 승인 없이 자동으로 파일을 덮어쓰지 않는다.

사용자가 승인하면:

1. `authors/{author_id}/style.yaml` 저장
2. `authors/{author_id}/theology.yaml` 저장
3. `authors/{author_id}/sermon_pattern.yaml` 저장
4. `authors/{author_id}/vocabulary.md` 저장

각 파일 저장 시 기존 파일은 내용을 병합하되, 분석 결과로 확정된 값을 우선한다.

### Step 9: 완료 리포트

```
저자 프로필이 {생성/갱신}되었습니다.

저자: {author.name}
분석 자료: {N}건 (wiki 기사 {a}건 + raw entries {b}건)
업데이트된 파일:
  - authors/{author_id}/style.yaml
  - authors/{author_id}/theology.yaml
  - authors/{author_id}/sermon_pattern.yaml
  - authors/{author_id}/vocabulary.md

이 프로필은 /publish-write, /publish-review, /publish-sermon에서
저자의 문체와 신학적 입장 기준으로 사용됩니다.

다음 단계: 새 책을 쓰거나 설교를 준비하려면 말씀해 주세요.
```

---

## 참조 문서

- `shared/references/author-profile-schema.md` — 저자 프로필 4파일 스키마 전체
- `shared/references/workspace-schema.md` — 워크스페이스 구조 + config.yaml 스키마
- `shared/references/search-strategy.md` — wiki/ 계층 검색 전략
- `shared/references/context-management.md` — 컨텍스트 윈도우 관리 전략 + 샘플링 패턴
- `publish-profile/references/analysis-dimensions.md` — 4차원 분석 상세 기준
