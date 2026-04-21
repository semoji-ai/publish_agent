---
name: author-profile-schema
description: Publish Agent 저자 프로필 4개 파일의 스키마 정의. theology.yaml, style.yaml, sermon_pattern.yaml, vocabulary.md의 전체 구조와 작성 규칙.
---

# 저자 프로필 스키마

저자 프로필은 `authors/{author_id}/` 디렉토리의 4개 파일로 구성된다. `/publish-profile` 스킬이 생성·갱신하며, `/publish-write`와 `/publish-review`가 참조한다.

**핵심 원칙:** 저자 프로필은 "올바른 신학"이나 "좋은 문체"의 기준이 아니라, **이 저자의 실제 특성**을 기록한다. 평가하거나 교정하지 않는다.

---

## 1. theology.yaml — 신학적 입장

저자의 신학적 포지션을 주요 교리 영역별로 기록한다.

### 스키마

```yaml
soteriology:                        # 구원론
  position: "개혁주의"              # 신학적 전통/입장 명칭
  emphasis: "은혜의 무조건성"       # 이 저자가 특별히 강조하는 관점
  key_texts:                        # 이 주제에서 저자가 자주 인용하는 성경 본문
    - "로마서 8:29-30"
    - "에베소서 2:8-9"
    - "요한복음 6:37-44"
  notes: "인간의 전적 타락과 하나님의 주권적 선택을 강조. 알미니안적 요소 배제."

eschatology:                        # 종말론
  position: "역사적 전천년설"
  emphasis: "그리스도의 인격적 재림"
  key_texts:
    - "데살로니가전서 4:16-17"
    - "요한계시록 20:1-6"
  notes: ""

ecclesiology:                       # 교회론
  position: "장로교 정치"
  emphasis: "말씀 중심 예배"
  key_texts:
    - "에베소서 4:11-12"
    - "마태복음 18:15-20"
  notes: "성례와 권징을 교회의 표지로 강조"

pneumatology:                       # 성령론
  position: "개혁주의 (은사중지론적 경향)"
  emphasis: "성령의 내적 조명과 성화 역할"
  key_texts:
    - "요한복음 16:13"
    - "로마서 8:9-17"
  notes: "표적 은사에 대해 신중한 입장. 성령의 말씀 조명 사역 강조."

scripture_view:                     # 성경관
  position: "무오성/축자영감"
  emphasis: "성경의 유일한 권위"
  key_texts:
    - "디모데후서 3:16-17"
    - "베드로후서 1:20-21"
  notes: ""

# 추가 신학 항목 (필요시)
covenant_theology:                  # 언약신학 (선택)
  position: ""
  emphasis: ""
  key_texts: []
  notes: ""

sacramentology:                     # 성례론 (선택)
  position: ""
  emphasis: ""
  key_texts: []
  notes: ""
```

### 필드 설명

| 필드 | 설명 | 비고 |
|------|------|------|
| `position` | 신학적 전통 또는 입장 명칭 | 가능한 한 표준 신학 용어 사용 |
| `emphasis` | 이 저자가 해당 교리에서 특별히 강조하는 측면 | 다른 개혁주의 신학자와의 차별점 |
| `key_texts` | 자주 인용하는 성경 구절 | 최대 5개 권장 |
| `notes` | 추가 맥락, 뉘앙스, 주의사항 | 선택. 비어있으면 `""` |

### 작성 주의사항

- `position`이 불명확할 경우 공란(`""`)으로 둠. 추측으로 채우지 말 것
- `notes`에 LLM의 평가나 권고 포함 금지 ("이 입장은 문제가 있다" 등)
- 분석 시 primary 자료(저자 본인 글)만 근거로 사용

---

## 2. style.yaml — 문체 프로필

저자의 글쓰기 스타일의 객관적 특성을 기록한다.

### 스키마

```yaml
tone: "경어체"                        # 문장 어투 (경어체 | 반말체 | 혼합 | 격식체)
sentence_length:
  average: "중간"                     # 짧음(~10자) | 중간(11-25자) | 긴편(26-40자) | 김(40+자)
  range: "15-25자"                    # 평균 범위 (문자 기준)
  tendency: "간결 선호"               # 자유 기술

rhetoric:
  metaphor_frequency: "높음"          # 매우 낮음 | 낮음 | 보통 | 높음 | 매우 높음
  favorite_metaphors:                 # 자주 사용하는 비유 소재/패턴
    - "빛과 어둠"
    - "씨앗과 열매"
    - "길과 여정"
    - "양과 목자"
  simile_frequency: "보통"
  repetition: "강조를 위한 반복 즐겨 씀"   # 반복법 사용 패턴
  rhetorical_questions: true          # 수사적 질문 사용 여부

argumentation: "연역적"               # 연역적 | 귀납적 | 혼합 | 예화 중심
paragraph_style: "짧은 단락 선호"    # 단락 구성 경향
transition_style: "명시적 전환어 사용" # 단락/섹션 전환 방식

vocabulary_level: "중간"              # 전문적 | 중간 | 일반적 (신학 용어 사용 정도)
formality: "격식적"                   # 격식적 | 반격식 | 비격식

sentence_patterns:                    # 특징적인 문장 구조 패턴
  - "~하는 것이 아니라, ~해야 한다"
  - "첫째... 둘째... 셋째..."
  - "왜냐하면 ~ 때문이다"
```

### 필드 설명

| 필드 | 설명 |
|------|------|
| `tone` | 청중에게 말하는 방식. 설교문과 저서가 다를 수 있으면 메모 |
| `sentence_length.range` | 대표적 문장 길이 범위 (문자 수, 한글 기준) |
| `rhetoric.favorite_metaphors` | 분석된 텍스트에서 3회 이상 등장한 비유 소재 |
| `argumentation` | 결론을 먼저 제시하고 근거를 나열하면 연역적, 사례에서 원칙으로 가면 귀납적 |
| `vocabulary_level` | `전문적`: 신학 원어(헬라어/히브리어) 빈번 사용, `일반적`: 쉬운 표현 선호 |

---

## 3. sermon_pattern.yaml — 설교 구조 패턴

저자의 설교 구성 방식을 기록한다. 설교문 자료(primary, category: sermon)를 기반으로 분석.

### 스키마

```yaml
structure: "귀납적"                   # 귀납적 | 연역적 | 내러티브 | 대화형 | 주제별 | 혼합

# 구성 비율 (합계 1.0)
intro_ratio: 0.15                     # 서론 비율
body_ratio: 0.65                      # 본론 비율
application_ratio: 0.20              # 적용/결론 비율

body_structure:
  points_count: "3포인트"             # 본론의 대지(大旨) 수 경향 (2포인트 | 3포인트 | 가변)
  point_pattern: "귀납적 전개"        # 각 대지 내부 전개 방식

illustration:
  frequency: "본론당 1-2회"           # 예화 빈도
  sources:                            # 주로 사용하는 예화 출처/유형
    - "개인 경험"
    - "교회사 일화"
    - "시사 사례"
    - "성경 내 다른 본문"
  placement: "대지 설명 후 예시"      # 예화 위치 (도입부 | 설명 후 | 적용 전)

scripture:
  citation_style: "본문 직접 인용 후 해설"    # 성경 인용 방식
  translation: "개역개정"            # 주로 사용하는 성경 번역본
  cross_reference_frequency: "높음"  # 다른 성경 구절 교차 인용 빈도
  original_language: false           # 헬라어/히브리어 직접 사용 여부

audience:
  address_style: "성도 여러분"       # 청중 호칭 방식
  direct_address: true               # "여러분", "우리"로 직접 대화 여부
  rhetorical_questions: "적극 사용"  # 청중에게 던지는 질문 사용 빈도

closing:
  style: "기도/결단 촉구"             # 마무리 방식
  invitation: true                   # 초청/결단 요청 포함 여부
```

### 분석 기준

- 최소 5편 이상의 설교 분석을 기반으로 작성
- 시기별로 패턴이 변했다면 `notes` 섹션에 추가 (`notes: "2020년 이전: 연역적, 이후: 귀납적"`)
- 비율(`intro_ratio` 등)은 실제 단어/줄 수 기준 측정값

---

## 4. vocabulary.md — 어휘 패턴

저자가 자주 쓰거나 피하는 표현, 성경 인용 방식, 특징적 어휘를 기록한다. YAML 대신 Markdown 형식으로 작성하여 가독성과 가변적 목록 관리에 최적화.

### 전체 구조

```markdown
# {author_id} 어휘 패턴

마지막 분석: {date}
분석 대상: {N}건 primary 자료

---

## 자주 쓰는 표현

빈도 순으로 정렬. 숫자는 분석된 자료에서의 등장 횟수.

- "은혜 가운데" (47회)
- "말씀이 선포될 때" (31회)
- "하나님의 주권" (28회)
- "우리가 기억해야 할 것은" (22회)
- "십자가 앞에서" (19회)
- "오직 은혜로" (17회)
- "성령의 역사" (15회)

---

## 피하는 표현

분석된 텍스트에서 거의 등장하지 않거나, 저자가 명시적으로 사용을 꺼리는 표현.

- "운명" (숙명론적 뉘앙스 회피)
- "에너지", "바이브" 등 현대 비속어/신조어
- "~하면 복 받는다" (번영신학적 표현)
- "느낌", "감동" (주관적 감정 위주 표현)

---

## 성경 인용 방식

### 번역본
- 1차: 개역개정
- 참고: 새번역 (독자 이해를 위해 병행 인용 시)
- 원어 직접 인용: 거의 없음

### 인용 형식
- 인용 시 큰따옴표 사용: "하나님이 세상을 이처럼 사랑하사" (요 3:16)
- 장절 표기: (책명 장:절) 형식, 예: (요 3:16), (롬 8:28)
- 긴 인용(3절 이상): 별도 들여쓰기 블록으로 처리

### 인용 맥락
- 설교: 본문 직접 인용 후 절별 해설
- 저서: 주장 근거로 인용 + 간략한 문맥 설명

---

## 특징적 전환어 및 접속어

### 설명 전환
- "다시 말해", "즉", "바꾸어 말하면"

### 논증 전환
- "왜냐하면", "그 이유는", "이것이 의미하는 바는"

### 대조 전환
- "그러나", "반면에", "하지만 여기서 주목할 것은"

### 강조
- "바로 이것이", "이 점이 핵심입니다", "무엇보다 중요한 것은"

---

## 특징적 신학 어휘

저자가 독특하게 사용하거나 특별히 강조하는 신학 용어.

- "은혜의 주권성" — 하나님의 선택과 구원의 절대적 주권 표현 시
- "말씀의 능력" — 설교와 성경의 효력 설명 시
- "언약의 백성" — 교회/신자 공동체를 지칭할 때
- "십자가의 어리석음" — 복음의 역설성 강조 시

---

## 개정 이력

| 날짜 | 변경 내용 | 분석 자료 수 |
|------|----------|------------|
| 2026-04-21 | 최초 생성 | 23건 |
```

### vocabulary.md 갱신 규칙

1. 새 자료 absorb 후 빈도가 크게 변한 항목은 재분석 시 업데이트
2. 새로 등장한 패턴은 기존 섹션에 추가 (삭제하지 않음)
3. 갱신 시 "개정 이력" 테이블에 날짜와 변경 내용 기록
4. 사용자 확인 없이 자동 덮어쓰기 금지 (/publish-profile의 diff 확인 후 승인)

---

## 5. 프로필 파일 초기화 (빈 템플릿)

`/publish-setup` 실행 시 생성되는 빈 템플릿. 분석 전 placeholder 상태.

### theology.yaml 초기 상태

```yaml
# {author_id} theology profile
# Created: {date}
# Status: empty — /publish-profile 실행 후 채워짐

soteriology:
  position: ""
  emphasis: ""
  key_texts: []
  notes: ""

eschatology:
  position: ""
  emphasis: ""
  key_texts: []
  notes: ""

ecclesiology:
  position: ""
  emphasis: ""
  key_texts: []
  notes: ""

pneumatology:
  position: ""
  emphasis: ""
  key_texts: []
  notes: ""

scripture_view:
  position: ""
  emphasis: ""
  key_texts: []
  notes: ""
```

### style.yaml 초기 상태

```yaml
# {author_id} style profile
# Created: {date}
# Status: empty — /publish-profile 실행 후 채워짐

tone: ""
sentence_length:
  average: ""
  range: ""
  tendency: ""
rhetoric:
  metaphor_frequency: ""
  favorite_metaphors: []
  simile_frequency: ""
  repetition: ""
  rhetorical_questions: null
argumentation: ""
paragraph_style: ""
transition_style: ""
vocabulary_level: ""
formality: ""
sentence_patterns: []
```

### sermon_pattern.yaml 초기 상태

```yaml
# {author_id} sermon pattern profile
# Created: {date}
# Status: empty — /publish-profile 실행 후 채워짐

structure: ""
intro_ratio: null
body_ratio: null
application_ratio: null
body_structure:
  points_count: ""
  point_pattern: ""
illustration:
  frequency: ""
  sources: []
  placement: ""
scripture:
  citation_style: ""
  translation: ""
  cross_reference_frequency: ""
  original_language: null
audience:
  address_style: ""
  direct_address: null
  rhetorical_questions: ""
closing:
  style: ""
  invitation: null
```

### vocabulary.md 초기 상태

```markdown
# {author_id} 어휘 패턴

마지막 분석: (미분석)
분석 대상: 0건

---

## 자주 쓰는 표현
(분석 후 채워짐)

---

## 피하는 표현
(분석 후 채워짐)

---

## 성경 인용 방식
(분석 후 채워짐)

---

## 특징적 전환어 및 접속어
(분석 후 채워짐)

---

## 특징적 신학 어휘
(분석 후 채워짐)

---

## 개정 이력

| 날짜 | 변경 내용 | 분석 자료 수 |
|------|----------|------------|
| (없음) | | |
```
