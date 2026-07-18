# 설교 팩 (Sermon Pack) — 측정 가능한 문체 학습·검증 설계

작성일: 2026-07-18
상태: 승인됨 (사용자 확인)

## 문제

현재 파이프라인은 규칙 발견(publish-profile 4차원)과 심사 기준(publish-review
rubric)은 있지만, **검증이 전부 LLM의 판단**이다. 프로필에 "평균 15어절"이라
적어도 초안이 실제 15어절인지 재는 코드가 없다. "목사님 설교를 학습하면 그
설교를 써나갈 수 있는가"에 측정 가능한 답이 없다.

## 해법: gn-voice 방법론 이식

gn-voice(개인 문체 윤문 시스템, 실증 완료)의 구조를 설교 도메인으로 가져온다:
코퍼스 실측 fingerprint → 수치 기반 팩 → **stdlib 기계 게이트** → LLM 심사.

```
설교 코퍼스 (raw/entries/ 또는 지정 폴더)
  → ① scripts/sermon_fingerprint.py  : 실측 지표 JSON
  → ② authors/{name}/sermon-pack.md  : 수치+근거 인용이 담긴 팩 (profile 스킬이 작성)
  → ③ publish-write/-sermon          : 팩을 집필 제약으로 로드
  → ④ scripts/verify_sermon.py       : 초안 실측 → 팩 대조 게이트 (ok:false면 재작성)
  → ⑤ publish-review                 : 게이트 통과본만 LLM rubric 심사
```

## ① sermon_fingerprint.py (신규, stdlib only)

입력: 설교 텍스트 폴더(.md/.txt, UTF-8). 출력: fingerprint JSON (stdout 또는 -o).

측정 항목 (형태소 분석기 없이 근사 — gn-voice와 동일 접근):
- `n_docs`, `n_sents`, 문장 어절 수 `p10/p50/p90/mean`
- 어미 분포: 문장 끝 어절의 종결 패턴 상대빈도 (습니다/ㅂ니다/어요·아요/죠/다/까/ㅂ시다/시오 등 정규식 매칭, `_other` 포함)
- 구두점 /1k자: 마침표·쉼표·물음표·느낌표·말줄임·인용부호
- 담화 마커 /1k어절: 첫째·둘째류, 그러나/하지만/그런데, 사랑하는 여러분 류 호칭(설정 가능 목록)
- 자기지칭 /1k어절: 저/제가/나/우리
- 성경 인용 밀도: 인용 패턴(「」, "", (요 3:16) 류 장절 표기) /1k자
- 단락: 단락당 문장 수 p50, 빈 줄 비율

문장 분리: 종결부호+공백 기준, 장절 표기 괄호는 보호. 인용문 내부는 측정에서
제외하지 않음(설교는 인용도 문체의 일부) — 단순화 결정.

## ② sermon-pack.md 스키마 (shared/references/sermon-pack-schema.md)

gn-voice 팩 해부 구조를 설교용 6섹션으로:
1. **레지스터** — 화계·어미 골격 (fingerprint 수치 인용)
2. **시그니처** — 즐겨 쓰는 표현 표(표현/기능/실측 빈도/근거 설교 id)
3. **리듬** — 문장 어절 분포, 단락, 구두점
4. **설교 구조 관습** — 도입·본문 전개·예화 배치·적용·마무리 패턴 (근거 인용)
5. **대조페어** — "일반적 설교투 → 이 목사님 방식" 변환 예시 5개+
6. **Do-NOT** — 실측 0회 패턴, AI 상투구, 피하는 표현 (vocabulary.md 연동)

팩은 `/publish-profile`이 fingerprint JSON + 코퍼스 인용을 근거로 작성한다
(스킬 지침 추가). 모든 수치는 fingerprint 실측만 인용 — 추정 금지.

## ③ verify_sermon.py (신규, stdlib only) — 기계 게이트

입력: 초안 파일 + fingerprint.json + rules.json. 출력: `{"ok": bool, "violations": [...]}`, exit 0/1.

rules.json (팩과 함께 profile이 생성, 스키마 고정):
```json
{
  "bands": {"sent_p50": [저, 고], "ending_top1_share": [저, 고],
             "question_per_1k": [저, 고], "exclam_per_1k": [저, 고]},
  "must_zero": ["결론부터 말씀드리면", "요약하자면", ...],
  "signatures": [{"expr": "사랑하는 성도 여러분", "min_per_doc": 1}, ...],
  "ai_tells": [기본 목록 내장 + 추가]
}
```
검사: 1) 범위(bands) — 초안 실측치가 밴드 밖이면 위반 2) must_zero — 1건도
발견 시 위반 3) ai_tells 상투구 — 발견 시 위반 4) signatures — min 미달 시 위반.
위반마다 `{check, expected, actual, evidence(해당 문장)}`.

기본 ai_tells 내장 목록(한국어 설교·산문 공통): "결론부터 말씀드리면",
"요약하자면", "다음과 같습니다", "~라고 할 수 있습니다", "이번 시간에는",
"함께 살펴보겠습니다", "마무리하겠습니다" 등 — rules.json에서 가감 가능.

## ④⑤ 스킬 연동 (기존 SKILL.md 수정 — 코어 main)

- `publish-profile`: 분석 단계에 fingerprint 실행 + sermon-pack.md/rules.json
  생성 추가. custom-sermon-pack.md 있으면 우선(브랜치 규칙 준수).
- `publish-write`(설교집/강해서 모드)·`publish-sermon`: 팩 존재 시 제약으로
  로드하고, 초안 완료 후 verify_sermon.py 실행 → ok:false면 위반 목록 기반
  재작성(최대 2회) 후에도 실패 시 위반 명시하고 사용자에게 보고.
- `publish-review`: 심사 1단계로 게이트 결과 확인(미실행이면 실행), rubric
  문체 심사는 게이트 통과 후 수행. 리포트에 기계 실측치 표 포함.

## 학습 루프 (범위 제한)

목사님 교정 반영 자동화는 kairos-studio P3 소관. 여기서는 수동 경로만 문서화:
교정이 쌓이면 `/publish-profile` 재실행으로 팩 갱신(코퍼스에 최신 설교 추가).

## 완료 기준

1. 합성 설교 코퍼스로 fingerprint JSON이 실측치를 낸다 (pytest)
2. 팩 밴드를 위반한 초안 → verify ok:false + 위반 근거 문장, 준수 초안 → ok:true
3. 실제 설교 샘플 1편으로 E2E: fingerprint → rules 생성 → 위반/준수 초안 판정
4. SKILL.md 3종에 게이트 단계가 문서화됨 (church 브랜치 merge 안전: 기존 파일
   수정은 최소 diff, 커스텀은 custom-* 우선 규칙 유지)

## 제외 (YAGNI)

- 형태소 분석기 의존(kiwi 등) — stdlib 근사로 시작, 정밀도 필요 시 후행
- 교정 자동 반영, 신학 내용 검증(그건 review rubric의 신학 차원 몫), 매끈함
  밴드(gn-voice smoothness — 설교 코퍼스 확보 후 후행)
