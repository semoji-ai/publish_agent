# Publish Agent Windows 후속 리뷰 및 수정 제안

작성일: 2026-04-22
대상: Claude에게 전달할 후속 수정 지시 문서
범위: Windows 실행 가능성 관련 잔여 이슈

## 요약

이전 수정으로 큰 방향은 좋아졌다.

- `pandoc -f pdf` 허위 fallback 제거
- `draft_file` / `slug` 추가
- Windows BOM / CP949 / 경로 정규화 문서화
- Windows 설치 확인 섹션 추가

하지만 아직 Windows에서 "바로 실행 가능"하다고 보기는 어렵다.
이번 라운드에서 남은 핵심 이슈는 3개다.

1. setup가 만드는 기본 `encoding` 값이 여전히 `utf-8`
2. Windows Python 실행 계약이 문서마다 다름
3. setup의 필수 도구 실패 처리 규칙이 모호함

---

## Findings

### 1. Windows 기본 설정이 여전히 `encoding: utf-8`

심각도: 높음

문제:
- setup가 생성하는 `config.yaml` 기본값이 `encoding: utf-8`이다.
- 공용 스키마도 동일하다.
- 그런데 Windows 인코딩 가이드는 한국어 Windows 기본 인코딩이 CP949이고, Windows 사용자에게는 `auto`를 권장한다고 적혀 있다.
- collect는 `defaults.encoding: utf-8`이면 감지를 생략한다.

증거:
- `skills/publish-setup/SKILL.md:136-140`
- `skills/shared/references/workspace-schema.md:93-97`
- `skills/shared/references/platform-tools.md:248-251`
- `skills/publish-collect/SKILL.md:127-131`

영향:
- Windows 사용자가 setup 직후 CP949 텍스트를 collect할 때, 문서가 새로 만든 자동 감지 경로를 타지 않고 바로 깨질 수 있다.

수정 제안:

권장안:
- Windows에서 setup 실행 시 `defaults.encoding` 기본값을 `auto`로 생성
- macOS/Linux는 기존 `utf-8` 유지 가능

최소 수정:
- `publish-setup`의 config.yaml 예시를 OS별로 분기하거나,
- 최소한 문장으로 "Windows면 기본값을 `auto`로 설정"을 명시

함께 수정할 파일:
- `skills/publish-setup/SKILL.md`
- `skills/shared/references/workspace-schema.md`
- `docs/specs/2026-04-21-publish-agent-design.md`

---

### 2. Windows Python 실행 계약이 아직 일관되지 않음

심각도: 중간

문제:
- setup는 Windows 필수 Python 확인을 `py -3 --version` 또는 `python --version`으로 적어두었다.
- 하지만 공통 플랫폼 문서와 collect reference는 Windows에서 "반드시 `py -3`"를 기준으로 쓴다.
- 설치 확인 문서도 `py -3 --version`만 보여준다.

증거:
- `skills/publish-setup/SKILL.md:58-59`
- `skills/shared/references/platform-tools.md:236`
- `skills/publish-collect/references/format-handling.md:239-241`
- `CLAUDE.md:38-43`

영향:
- `python`만 있고 `py`가 없는 Windows 환경은 setup는 통과해도 collect 예시나 설치 확인 단계에서 다시 막힐 수 있다.
- 반대로 `py -3`만 있는 환경을 기준으로 한다면 setup도 그렇게 고정해야 한다.

수정 제안:

둘 중 하나를 명확히 선택할 것.

권장:
- Windows 표준 실행 계약을 `py -3`로 통일
- setup도 `python --version` 대안을 빼고 `py -3` 기준으로 맞춤

대안:
- `py -3` 우선, 없으면 `python`
- 이 경우 모든 문서에서 동일한 우선순위를 반복해야 함

권장 수정 방향:
- 가장 단순하게 `py -3` 단일 기준으로 통일

함께 수정할 파일:
- `skills/publish-setup/SKILL.md`
- `skills/shared/references/platform-tools.md`
- `skills/publish-collect/references/format-handling.md`
- `CLAUDE.md`

---

### 3. setup의 필수 도구 실패 처리 규칙이 모호함

심각도: 중간

문제:
- setup 본문 끝에 남아 있는 규칙 문장이 아직 메모 수준이다.
- "필수 도구가 없으면 경고 후 계속"이라고 하면서, pandoc과 Windows Python은 예외라고 적고,
- 바로 다음 줄에서는 Python이 없으면 강한 경고를 주라고만 적는다.

증거:
- `skills/publish-setup/SKILL.md:92-93`

영향:
- 구현자나 모델이 "Windows Python이 없으면 중단인지, 경고 후 진행인지"를 다르게 해석할 수 있다.
- readiness 점검기의 핵심 역할이 흐려진다.

수정 제안:

이 부분을 자유 문장이 아니라 결정 규칙 표로 바꿀 것.

예시:

```text
필수 도구 실패 규칙

- pandoc 없음:
  setup 계속 가능
  collect 일부 가능
  export 불가

- Windows에서 py -3 없음:
  setup는 계속 가능
  하지만 Windows 텍스트 인코딩 fallback 불가
  collect 기능은 제한됨
  완료 리포트에 반드시 경고 표시

- pdftotext 없음:
  PDF collect 불가

- xelatex 또는 Noto Sans KR 없음:
  PDF export 불가
```

중요:
- "continue / warn / block" 중 어느 동작인지 문장으로 남기지 말고 명시적 표로 정의할 것

함께 수정할 파일:
- `skills/publish-setup/SKILL.md`

---

## Claude에게 제안하는 수정 순서

### P0

Windows setup 기본값을 `encoding: auto`로 바꿀 것.

### P1

Windows Python 실행 계약을 하나로 통일할 것.

권장:
- `py -3` 단일 기준

### P2

setup의 실패 처리 규칙을 표로 바꿔서 해석 여지를 없앨 것.

---

## 수정 완료 기준

아래 질문에 모두 "예"라고 답할 수 있어야 한다.

1. Windows에서 setup 직후 생성되는 `config.yaml`이 CP949/BOM 환경을 안전하게 처리할 기본값을 가지는가?
2. Windows Python 실행 방식이 `publish-setup`, `platform-tools`, `format-handling`, `CLAUDE.md` 전부에서 일치하는가?
3. setup 문서만 읽어도 어떤 의존성 부족은 계속 진행 가능하고, 어떤 기능은 제한되는지 명확히 알 수 있는가?

---

## 짧은 결론

이제 남은 문제는 구조적이라기보다 계약 정리 문제다.

- Windows 기본값
- Windows Python 실행 방식
- setup 실패 처리 규칙

이 세 가지만 정리하면 Windows 문서는 "고려됨" 수준에서 "실행 지향" 수준으로 올라간다.
