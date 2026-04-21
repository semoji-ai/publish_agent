# Publish Agent Windows 실행 가능성 리뷰 및 수정 제안

작성일: 2026-04-22
대상: Claude에게 전달할 Windows 지원 작업 지시 문서
범위: `projects/publish_agent`의 Windows 실행 가능성만 집중 검토

## 결론

현재 상태는 "Windows 관련 문구와 예시는 꽤 보강되었지만, 아직 Windows에서 바로 실행 가능한 수준은 아님"이다.

좋아진 점:
- 설치 문서에 Windows 링크/명령이 추가됨
- `pandoc -f pdf` 허위 fallback 제거
- `draft_file` 기반 export 매핑 추가
- Windows 경로 정규화와 BOM/CP949 이슈를 문서에 반영함

하지만 아직 남아 있는 핵심 문제:
- Windows 수집 경로가 `python3`와 `chardet`를 사실상 필수로 가정하는데 setup가 이를 준비시키지 않음
- Windows 전용 명령 예시는 있지만 "어떤 런타임을 최소 전제로 둘 것인가"가 정해져 있지 않음
- setup 단계가 Windows collect/export에 필요한 의존성 검증을 하지 않음

즉, 지금은 "Windows 고려 문서" 수준이지 "Windows 실행 보장 문서" 수준은 아니다.

---

## Windows 목표 상태

Claude가 수정 후 다음 시나리오가 실제로 가능해야 한다.

1. Windows에서 `publish-setup` 실행
2. CP949 또는 UTF-8 BOM이 섞인 `.txt` 파일 수집
3. `.docx` 수집
4. 텍스트 기반 `.pdf` 수집
5. 초안 작성 후 DOCX export
6. 추가 의존성 설치 시 PDF export

이 목표를 기준으로 보면, 현재 문서는 아직 아래 항목들이 비어 있다.

---

## 핵심 Findings

### 1. Windows collect 경로가 `python3`와 `chardet`에 과도하게 의존함

심각도: 높음

문제:
- Windows 인코딩 감지는 `python3 -c "import chardet ..."`를 기본 경로로 잡고 있다.
- 변환도 `python3` 기반이다.
- 그런데 setup 문서는 `pandoc`만 확인하고 끝난다.

증거:
- `skills/publish-collect/references/format-handling.md:221-226`
- `skills/publish-collect/references/format-handling.md:265-286`
- `skills/shared/references/platform-tools.md:226-227`
- `skills/shared/references/platform-tools.md:236`
- `skills/publish-setup/SKILL.md:47-66`

문제의 본질:
- Windows 기본 환경에 `python3` 명령이 항상 있는 것이 아니다.
- 많은 Windows 환경에서는 `py -3`는 있어도 `python3`는 없다.
- `chardet`는 표준 라이브러리가 아니므로 기본 설치도 아니다.

영향:
- `defaults.encoding: auto` 경로가 실제 사용자 환경에서 바로 막힐 수 있다.
- collect의 핵심 가치인 "Windows에서 CP949 텍스트도 처리"가 보장되지 않는다.

수정 제안:

필수 결정:
- Windows 최소 런타임을 하나 정할 것.

권장안:
- Windows 최소 전제: `py -3` 또는 `python`
- `python3`는 필수 명령으로 가정하지 말 것

구체 수정:
1. `format-handling.md`와 `platform-tools.md`의 Windows 예시에서 `python3`를 제거
2. Windows Python 실행 예시는 다음 우선순위로 서술
   - `py -3`
   - `python`
3. `chardet`를 선택 의존성으로 내리고, 없을 때 동작하는 stdlib fallback를 제공

권장 fallback 순서:
1. BOM 확인
2. UTF-8 시도
3. CP949 시도
4. EUC-KR 시도
5. 마지막에 `errors='replace'`

즉, `chardet` 없이도 최소 수집은 되게 해야 한다.

대상 파일:
- `skills/publish-collect/references/format-handling.md`
- `skills/shared/references/platform-tools.md`
- `skills/publish-collect/SKILL.md`

---

### 2. `publish-setup`가 Windows 필수 전제조건을 검증하지 않음

심각도: 높음

문제:
- setup는 현재 `pandoc`만 확인한다.
- 하지만 Windows 실행 가능성을 보장하려면 collect/export 관점에서 더 많은 사전 점검이 필요하다.

증거:
- `skills/publish-setup/SKILL.md:47-66`

누락된 Windows 체크 항목:
- Python 런처 존재 여부: `py -3` 또는 `python`
- `pdftotext` 존재 여부
- PDF export용 `xelatex` 존재 여부
- PowerShell 사용 가능 여부

영향:
- setup가 성공해도 collect/export가 나중에 바로 실패한다.
- 사용자는 "설치는 끝났다"고 생각하지만 실제로는 준비가 안 된 상태다.

수정 제안:

`publish-setup`의 의존성 확인을 2단계로 분리:

1. 기본 필수
- `pandoc`
- Windows인 경우 `py -3` 또는 `python`

2. 선택 기능 의존성
- PDF collect: `pdftotext`
- PDF export: `xelatex`, Noto Sans KR

출력 예시:

```text
Windows 환경 점검 결과

기본 기능:
  [OK] pandoc
  [OK] py -3

선택 기능:
  [MISSING] pdftotext  -> PDF 수집 불가
  [MISSING] xelatex    -> PDF export 불가
  [MISSING] Noto Sans KR -> 한글 PDF export 불가
```

핵심:
- setup는 "지금 가능한 기능 / 아직 불가능한 기능"을 분리해서 알려줘야 한다.

대상 파일:
- `skills/publish-setup/SKILL.md`

---

### 3. Windows 인코딩 처리 문서는 늘었지만, 실행 계약이 아직 불명확함

심각도: 높음

문제:
- 문서는 Windows가 CP949, BOM 이슈를 가진다는 점을 잘 설명한다.
- 하지만 실제로 어떤 로직을 우선 사용해야 하는지, 표준 경로가 무엇인지가 문서 전체에서 합의되지 않았다.

증거:
- `skills/shared/references/platform-tools.md:243-282`
- `skills/publish-collect/SKILL.md:127-133`
- `skills/publish-collect/references/format-handling.md:178-286`

현재 문제:
- 한 문서에서는 `chardet`를 권장
- 다른 문서에서는 Python fallback
- setup는 둘 다 설치 확인 안 함

수정 제안:

Windows 인코딩 처리의 단일 기준을 정할 것.

권장 기준:
- `chardet`는 선택
- 기본 경로는 표준 라이브러리만 사용

권장 알고리즘:
1. 바이너리로 읽기
2. UTF-8 BOM 제거
3. UTF-8 decode 시도
4. CP949 decode 시도
5. EUC-KR decode 시도
6. 실패 시 `replace`

이 로직을 다음 두 파일에 같은 표현으로 넣을 것:
- `skills/shared/references/platform-tools.md`
- `skills/publish-collect/references/format-handling.md`

그리고 `publish-collect/SKILL.md`에는 요약만 남길 것.

---

### 4. Windows 설치 문구가 생겼지만 "설치 후 검증" 단계가 없다

심각도: 중간

문제:
- `CLAUDE.md`와 각 스킬 문서에 Windows 설치 명령이 늘었지만,
- 실제로 설치가 끝난 뒤 성공 여부를 확인하는 smoke test가 없다.

증거:
- `CLAUDE.md:30-33`
- `skills/publish-export/SKILL.md:59-64`
- `skills/publish-collect/references/format-handling.md:89-95`

영향:
- 사용자는 `choco install poppler`, `winget install pandoc` 등을 수행해도 PATH 문제로 바로 실패할 수 있다.
- Windows는 재로그인/새 PowerShell 세션이 필요한 경우가 많다.

수정 제안:

Windows 전용 smoke test 섹션을 추가할 것.

예시:

```powershell
pandoc --version
py -3 --version
pdftotext -v
xelatex --version
```

그리고 결과 해석까지 명시:
- `pandoc` 없음 -> DOCX/ePub/PDF export 불가
- `py -3` 없음 -> Windows 인코딩 fallback 불가
- `pdftotext` 없음 -> PDF collect 불가
- `xelatex` 없음 -> PDF export 불가

대상 파일:
- `CLAUDE.md`
- `skills/publish-setup/SKILL.md`

---

### 5. `publish-export`의 Windows 지원은 문구상 좋아졌지만 여전히 "실행 흐름"이 덜 닫힘

심각도: 중간

문제:
- Windows용 MiKTeX/Noto Sans KR 안내는 추가되었다.
- 하지만 실제 Windows에서 어떤 명령으로 확인하고, 실패 시 어떤 포맷으로 폴백할지에 대한 흐름이 여전히 약하다.

증거:
- `skills/publish-export/SKILL.md:70-118`

세부 문제:
- 포맷은 Step 2에서 정하는데, Step 1은 포맷 의존성 점검을 먼저 하겠다고 적음
- PDF 대안을 제시하면서 실제 분기는 DOCX만 명시
- ePub만 원하는 사용자의 경로가 불명확

수정 제안:

`publish-export`의 흐름을 아래 순서로 재구성:

1. 프로젝트 선택
2. 포맷 선택
3. 선택한 포맷별 의존성 점검
4. 의존성 누락 시 가능한 대체 포맷만 제안
5. 사용자 승인 후 실행

특히 폴백 문구를 아래처럼 구체화:

```text
PDF는 지금 생성할 수 없습니다.
현재 가능한 포맷:
  - DOCX
  - ePub
어떤 포맷으로 계속할까요?
```

대상 파일:
- `skills/publish-export/SKILL.md`

---

### 6. Windows 경로 저장 규칙은 좋아졌지만, "명령 실행 시 변환" 규칙이 아직 느슨함

심각도: 중간

문제:
- 내부 저장은 `/` 구분자로 통일하겠다고 적어두었다.
- 하지만 실제 Windows 셸 실행 시 언제 `\`로 바꾸는지, 어떤 레이어가 책임지는지가 분명하지 않다.

증거:
- `skills/shared/references/platform-tools.md:272-282`
- `skills/publish-collect/SKILL.md:133`

영향:
- 문서 저장은 잘 돼도 실제 Windows 명령 실행에서 경로 quoting이 깨질 수 있다.

수정 제안:

실행 계약을 명확히 정의할 것:

- 저장 계층:
  - YAML/JSON/frontmatter에는 항상 `/`
- 실행 계층:
  - Windows 네이티브 명령 호출 직전에만 OS 경로로 변환
  - Python 내부 파일 접근은 `/` 그대로 허용 가능
  - PowerShell 네이티브 명령 예시는 quoting 포함

예시:

```powershell
$nativePath = $storedPath -replace '/', '\'
pdftotext -layout "$nativePath" -
```

대상 파일:
- `skills/shared/references/platform-tools.md`
- `skills/publish-collect/references/format-handling.md`

---

## Claude에게 제안하는 수정 순서

### P0. Windows 최소 실행 계약 확정

먼저 아래 중 하나를 명시적으로 선택할 것.

권장:
- Windows 최소 전제:
  - PowerShell
  - `py -3` 또는 `python`
  - `pandoc`
- 선택 전제:
  - `pdftotext`
  - `xelatex`
  - Noto Sans KR

이 계약이 없으면 이후 문서가 계속 흔들린다.

### P1. collect 경로를 `chardet` 비의존으로 재작성

해야 할 일:
- `chardet`를 보조 수단으로 내림
- 기본 인코딩 처리 경로를 stdlib-only로 재작성
- Windows 예시의 `python3`를 `py -3`/`python` 기준으로 수정

대상 파일:
- `skills/publish-collect/references/format-handling.md`
- `skills/shared/references/platform-tools.md`
- `skills/publish-collect/SKILL.md`

### P2. setup를 Windows readiness 점검기로 확장

해야 할 일:
- `pandoc`만 보는 현재 구조를 확장
- Windows에서 `py -3`, `pdftotext`, `xelatex` 상태를 나눠 보여주기
- setup 완료 리포트에 "지금 가능한 기능 / 불가능한 기능" 추가

대상 파일:
- `skills/publish-setup/SKILL.md`

### P3. export 흐름 재정렬

해야 할 일:
- 프로젝트 선택
- 포맷 선택
- 포맷별 의존성 확인
- 가능한 대체 포맷 제안

대상 파일:
- `skills/publish-export/SKILL.md`

### P4. Windows smoke test 추가

해야 할 일:
- `CLAUDE.md` 또는 `publish-setup`에 Windows 전용 검증 섹션 추가
- 사용자가 설치 직후 실행해볼 명령 제공

권장 명령:

```powershell
pandoc --version
py -3 --version
pdftotext -v
xelatex --version
```

대상 파일:
- `CLAUDE.md`
- `skills/publish-setup/SKILL.md`

---

## 수정 완료 기준

Claude가 수정 후 아래 질문에 모두 "예"라고 답할 수 있어야 한다.

1. Windows에서 `publish-setup` 실행 후 현재 가능한 기능과 불가능한 기능이 분리되어 보이는가?
2. Windows collect가 `chardet` 없이도 CP949/BOM 파일을 최소한 처리할 수 있는가?
3. Windows 문서에서 `python3`를 당연하게 가정하지 않는가?
4. PDF collect와 PDF export의 Windows 의존성이 setup 또는 smoke test에서 사전에 드러나는가?
5. Windows 경로를 내부 저장 형식(`/`)과 실행 형식(`\`)으로 분리해 설명하는가?
6. PDF가 불가할 때 DOCX/ePub 등 가능한 대체 포맷을 정확히 제안하는가?

---

## 짧은 결론

Windows 실행 가능성을 만들려면 "Windows 예시를 문서에 넣는 것"만으로는 부족하다.
핵심은 세 가지다.

1. Windows 최소 런타임 계약을 명확히 정할 것
2. collect 인코딩 경로를 추가 패키지 없이도 동작하게 만들 것
3. setup를 실제 readiness 점검기로 바꿀 것

이번 작업은 문구 개선이 아니라, Windows에서 첫 실행이 실제로 지나가게 만드는 작업으로 다뤄야 한다.
