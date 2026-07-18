# 설교 팩 스키마 (sermon-pack.md + sermon-rules.json)

`/publish-profile`이 `scripts/sermon_fingerprint.py`의 실측 JSON을 근거로
`authors/{author_id}/sermon-pack.md`와 `authors/{author_id}/sermon-rules.json`을
생성할 때 따르는 스키마다. gn-voice 팩 해부 구조(레지스터·시그니처·리듬·구조
관습·대조페어·Do-NOT)를 설교 도메인으로 이식한 것 — 참고: gn-voice
`references/packs/biz-l.md`.

## 원칙

- **수치는 fingerprint 실측만 인용, 추정 금지.** 팩의 모든 숫자는
  `sermon-fingerprint.json`의 값을 그대로 인용하거나 그 값에서 도출한
  계산(예: 밴드 = 실측치 ± 20%)이어야 한다. "대략", "느낌상" 같은 추정치를
  적지 않는다. 표본이 적으면(예: n_docs < 10) 그 사실을 팩에 명시하고
  "방향 위주, 개별 수치 과신 금지"로 경고한다.
- **custom-sermon-pack.md 우선.** `authors/{author_id}/custom-sermon-pack.md`가
  존재하면 이 표준 스키마보다 **우선 적용**한다 (교회 브랜치별 커스텀 규칙
  — publish-write/publish-review의 custom-modes.md·custom-rubric.md와 동일한
  패턴). custom 파일이 없으면 이 문서의 6섹션 구조를 기본으로 사용한다.

## sermon-pack.md — 6섹션 구조

### 1. 레지스터

화계(존댓말/반말)와 어미 골격을 fingerprint `endings` 딕셔너리로 인용한다.

```
예) 화계: 습니다 0.42 + ㅂ니다 0.18 = 존댓말 계열 0.60(ending_family_share).
   종결 골격: 습니다(0.42) > 다(0.15) > 죠(0.08) > 어요/아요(0.05).
```

### 2. 시그니처

즐겨 쓰는 표현을 표로 정리한다. 각 행은 표현 / 기능 / 실측 빈도(코퍼스 내
등장 횟수 또는 /1k어절) / 근거 설교 id(또는 파일명)로 구성한다.

```
| 표현 | 기능 | 실측 빈도 | 근거 |
|---|---|---|---|
| 사랑하는 성도 여러분 | 호칭·환기 | vocative 3.2/1k어절 | sermon_2024_03.md |
```

### 3. 리듬

fingerprint `sent_words`(p10/p50/p90/mean), `punct_per_1k`, 단락 지표
(`para_sents_p50`, `blank_ratio`)를 인용해 문장 길이·단락 호흡을 서술한다.

### 4. 설교 구조 관습

도입·본문 전개·예화 배치·적용·마무리의 반복 패턴을 코퍼스 인용과 함께
서술한다 (sermon_pattern.yaml과 중복 가능 — 여기서는 fingerprint의 담화
마커(`ordinal`, `adversative`, `vocative`) 실측치로 뒷받침한다).

### 5. 대조페어

"일반적 설교투 → 이 목사님 방식" 변환 예시를 **5개 이상** 제시한다. 각
예시는 흔한 AI/일반 설교투 표현 하나와 이를 대체할 저자 특유 표현/구조를
짝지은 것.

```
1. "결론부터 말씀드리면" → 도입 없이 성경 본문 낭독으로 바로 진입
2. "요약하자면" → "다시 한번 말씀드리지만"
...
```

### 6. Do-NOT

- 코퍼스 실측 0회 패턴 (fingerprint `endings`/`markers_per_1k_words`에서
  등장하지 않는 항목)
- AI 상투구 (`scripts/verify_sermon.py`의 `DEFAULT_AI_TELLS` 참고)
- `vocabulary.md`의 "피하는 표현" 절과 연동

## sermon-rules.json 스키마

`scripts/verify_sermon.py`가 소비하는 게이트 규칙. profile 스킬이 fingerprint
JSON을 근거로 생성한다.

```json
{
  "bands": {
    "sent_p50": [저, 고],
    "ending_family_share": [저, 고],
    "question_per_1k": [저, 고],
    "exclam_per_1k": [저, 고]
  },
  "must_zero": ["결론부터 말씀드리면", "요약하자면"],
  "signatures": [
    {"expr": "사랑하는 성도 여러분", "min_per_doc": 1}
  ],
  "ai_tells": ["추가 상투구 (DEFAULT_AI_TELLS에 합산됨)"]
}
```

- **`bands`**: 초안 실측치가 이 범위를 벗어나면 위반. 기본값은
  `fingerprint` 실측치의 **±20%**를 저/고 경계로 사용한다.
  - `ending_family_share`는 fingerprint `endings` 중 **습니다 + ㅂ니다**
    두 버킷의 합이다 (두 어미 계열을 하나의 존댓말 골격으로 묶어 잰다 —
    literal한 한 단어 종결 패턴이 아니라 family 합산임에 주의).
  - `sent_p50`은 `sent_words.p50`, `question_per_1k`/`exclam_per_1k`는
    `punct_per_1k.question`/`.exclam`에서 가져온다.
- **`must_zero`**: 코퍼스에 0회 등장해야 하는 문자열. 1건이라도 발견되면
  위반. vocabulary.md의 "피하는 표현"에서 채운다.
- **`signatures`**: 문서당 최소 등장 횟수(`min_per_doc`)를 강제하는 표현.
  시그니처 섹션의 상위 표현 중에서 고른다.
- **`ai_tells`**: `DEFAULT_AI_TELLS`(스크립트 내장)에 **추가**되는 목록.
  기본 목록을 대체하지 않고 합산된다.

## 생성 절차 (publish-profile 연동)

1. `python3 scripts/sermon_fingerprint.py <설교 코퍼스 경로> -o authors/{author_id}/sermon-fingerprint.json`
2. fingerprint JSON을 근거로 위 6섹션 `sermon-pack.md` 작성 (수치 인용 필수)
3. fingerprint JSON의 밴드 대상 지표에서 ±20% 범위를 계산해 `sermon-rules.json`
   작성 (`must_zero`는 vocabulary.md, `signatures`는 시그니처 섹션 상위 항목에서)
4. `authors/{author_id}/custom-sermon-pack.md`가 있으면 이 표준 스키마 대신
   해당 파일의 지침을 우선 적용
