# Publish Agent 리뷰 결과 및 수정 제안

작성일: 2026-04-22
대상: Claude에게 전달할 수정 지시 문서
범위: `projects/publish_agent` 전체 구조, 스킬 문서 일관성, macOS/Windows 호환성

## 요약

현재 저장소는 아이디어와 워크플로우 설계는 구체적이지만, 실제 설치/실행 기준으로 보면 다음 문제가 크다.

1. 스킬 설치 방식과 스킬 내부 참조 경로가 맞지 않아 reference 문서를 실제로 못 찾는다.
2. PDF 수집 fallback가 문서상 존재하지만 실제로는 성립하지 않는다.
3. `Claude Code / Codex / Gemini CLI 호환` 및 macOS/Windows 호환 표기가 실제 구현 상태보다 앞서 있다.
4. macOS는 추가 의존성 설치 후 부분 사용 가능하지만, Windows는 현재 기준으로 사실상 미지원이다.
5. `publish-write`와 `publish-export` 사이의 draft 매핑 규칙이 취약하다.

이 문서는 단순 리뷰가 아니라, Claude가 바로 수정에 들어갈 수 있도록 파일별 수정 제안을 함께 포함한다.

---

## 우선순위

### P0

- 지원 범위를 먼저 명확히 결정할 것
- broken reference path 수정
- 허위 fallback 제거
- 호환성 문구를 실제 상태와 맞출 것

### P1

- macOS/Linux/Windows별 의존성 및 대체 명령 정리
- export 사전 점검 강화
- 설치 문서와 스킬 참조 규칙 통일

### P2

- draft 파일 식별자 체계 보강
- 플랫폼 추상화 문서를 실제 상태에 맞게 갱신

---

## 핵심 Findings

### 1. 스킬 설치 방식과 내부 참조 경로가 충돌함

심각도: 높음

문제:
- `CLAUDE.md`는 각 스킬 디렉토리를 개별 심볼릭 링크하고, shared는 `publish-shared`로 따로 링크하게 되어 있다.
- 그런데 각 `SKILL.md`는 `shared/references/...` 또는 `publish-write/references/...` 같은 경로를 직접 참조한다.
- 이 구조에서는 설치 후 각 스킬 디렉토리 내부에서 해당 경로가 존재하지 않는다.

증거:
- `CLAUDE.md:23-33`
- `skills/publish-setup/SKILL.md:229-230`
- `skills/publish-write/SKILL.md:58,239-242`
- `skills/publish-profile/SKILL.md:85,286-289`
- `skills/publish-review/SKILL.md:186-189`
- `skills/publish-absorb/SKILL.md:348-352`

영향:
- 설치는 되어도 참조 문서를 열지 못해 실제 워크플로우가 중간에 끊긴다.
- 특히 `shared/references/...` 의존 스킬이 전부 영향을 받는다.

수정 제안:
- 둘 중 하나로 통일할 것.

안 1:
- 스킬 문서에서 참조 경로를 실제 설치 형태에 맞게 바꾼다.
- 예: `shared/references/workspace-schema.md` 대신 `../publish-shared/references/workspace-schema.md` 같은 방식으로 바꾸는 것은 플랫폼/실행기별로 더 불안정하므로 비추천.

안 2:
- 설치 방식을 바꿔서 `skills/` 전체를 하나의 루트로 노출하고 상대 참조가 실제로 살아 있게 만든다.
- 이 저장소 구조상 이쪽이 더 자연스럽다.

권장:
- 경로 표기를 "논리 참조명"으로 바꾸고, 실제 파일 탐색 규칙은 별도 문서에서 정의한다.
- 최소한 당장은 `CLAUDE.md` 설치 안내와 `platform-tools.md`의 참조 규칙을 함께 고쳐서 실제 설치 후 깨지지 않게 맞출 것.

대상 파일:
- `CLAUDE.md`
- `skills/shared/references/platform-tools.md`
- 모든 `skills/*/SKILL.md`의 참조 문서 섹션

---

### 2. PDF 수집 fallback가 허위 경로임

심각도: 높음

문제:
- 문서에서는 `pdftotext`가 없으면 `pandoc -f pdf -t markdown`로 대체하라고 적어두었다.
- 하지만 일반적인 pandoc은 PDF를 입력 포맷으로 지원하지 않는다.

증거:
- `skills/publish-collect/SKILL.md:140`
- `skills/publish-collect/references/format-handling.md:86-90`
- `skills/publish-collect/references/format-handling.md:333`

영향:
- `pdftotext`가 없는 환경에서 PDF 수집이 실패한다.
- 문서는 fallback가 있다고 말하지만 실제로는 실패하므로 운영자가 문제를 늦게 인지하게 된다.

수정 제안:
- `pandoc -f pdf` fallback를 완전히 제거할 것.
- fallback 대신 아래처럼 바꿀 것:

1. `pdftotext`가 있으면 사용
2. 없으면 즉시 안내 후 건너뜀
3. Windows/macOS/Linux별 설치 안내 제공
4. 이미지 PDF는 OCR 후 재수집하도록 명시

권장 문구:
- macOS: `brew install poppler`
- Ubuntu/Debian: `sudo apt install poppler-utils`
- Windows: poppler 배포본 또는 WSL 사용 안내

대상 파일:
- `skills/publish-collect/SKILL.md`
- `skills/publish-collect/references/format-handling.md`
- 필요 시 `docs/specs/2026-04-21-publish-agent-design.md`

---

### 3. Windows 호환 표기와 실제 구현 상태가 충돌함

심각도: 높음

문제:
- 상위 문서에서는 Claude/Codex/Gemini 및 다중 플랫폼 호환처럼 읽히지만,
- 실제 공통 참조 문서는 경로 구분자 `/`만 지원하며 Windows는 미지원이라고 적는다.
- 설치 방식도 `ln -sf`, `~/.claude/skills`, Unix 셸을 전제로 한다.

증거:
- `CLAUDE.md:50-51`
- `skills/shared/references/platform-tools.md:82-95`
- `skills/shared/references/platform-tools.md:208-212`
- `CLAUDE.md:23-33`

영향:
- Windows 사용자는 지원된다고 믿고 시작하지만 초기에 바로 막힌다.
- 문서 신뢰도가 떨어진다.

수정 제안:
- 지원 범위를 둘 중 하나로 확정할 것.

안 1: 현재 상태 기준 정직한 선언
- "현재 공식 지원: macOS/Linux"
- "Windows: 미지원 또는 실험적"

안 2: Windows 실제 지원
- PowerShell 설치/링크 절차 추가
- 경로 표기 규칙 보강
- Unix CLI 의존 명령에 대한 Windows 대체 경로 제공

권장:
- 이번 수정에서는 먼저 "macOS/Linux 우선 지원, Windows 미지원"으로 명시하는 것이 맞다.
- 이후 별도 작업으로 Windows 지원을 추가하는 편이 안전하다.

대상 파일:
- `CLAUDE.md`
- `skills/shared/references/platform-tools.md`
- `docs/specs/2026-04-21-publish-agent-design.md`

---

### 4. `publish-collect`가 Unix CLI에 강하게 결합되어 있음

심각도: 높음

문제:
- 인코딩 감지에 `file --mime-encoding`
- 인코딩 변환에 `iconv`
- 해시 계산에 `shasum -a 256`
- 설치에 `ln -sf`
- PDF 처리에 `pdftotext`

이 명령들은 macOS/Linux에서는 비교적 자연스럽지만 Windows 기본 환경에서는 바로 성립하지 않는다.

증거:
- `skills/publish-collect/SKILL.md:127-150`
- `skills/publish-collect/references/format-handling.md:172-215`
- `skills/publish-collect/references/format-handling.md:247-250`
- `CLAUDE.md:23-33`

영향:
- Windows 기본 환경에서 collect 파이프라인이 거의 전부 깨진다.
- macOS도 `pdftotext` 같은 추가 설치 항목은 빠져 있다.

수정 제안:
- OS별 명령 맵을 표로 추가할 것.

예시:
- 인코딩 감지
  - macOS/Linux: `file --mime-encoding`
  - Windows: Python fallback 또는 PowerShell/.NET 기반 판별
- 해시 계산
  - macOS: `shasum -a 256`
  - Linux: `sha256sum`
  - Windows PowerShell: `Get-FileHash -Algorithm SHA256`

중요:
- 공통 문서에서는 `sha256sum`을 예시로 들고 실제 스킬은 `shasum`을 쓰고 있으므로 이것도 통일해야 한다.

권장:
- 가능한 경우 명령 예시는 "행위 중심"으로 내리고, 구체 명령은 OS별 표로 분리한다.

대상 파일:
- `skills/publish-collect/SKILL.md`
- `skills/publish-collect/references/format-handling.md`
- `skills/shared/references/platform-tools.md`

---

### 5. PDF export 사전 점검이 불완전함

심각도: 중간

문제:
- `publish-export`는 Step 1에서 `pandoc`만 점검하고 진행한다.
- 하지만 PDF 생성은 `xelatex`와 `Noto Sans KR`에 의존한다.

증거:
- `skills/publish-export/SKILL.md:35-66`
- `skills/publish-export/SKILL.md:154-167`
- `skills/publish-export/SKILL.md:172-180`

영향:
- 사용자는 export가 가능한 줄 알고 진행하지만 PDF 단계에서야 실패한다.
- 특히 fresh macOS 환경에서는 바로 실패할 가능성이 높다.

수정 제안:
- Step 1을 포맷별 의존성 점검으로 바꿀 것.

예시:
- DOCX 선택 시: `pandoc`
- ePub 선택 시: `pandoc`
- PDF 선택 시:
  - `pandoc`
  - `xelatex`
  - CJK 폰트 존재 확인

또한 Windows 안내도 채워야 한다.

대상 파일:
- `skills/publish-export/SKILL.md`

---

### 6. `publish-write`와 `publish-export` 사이 draft 식별 규칙이 약함

심각도: 중간

문제:
- `project.yaml`의 `outline`은 `title`, `status`만 가진다.
- `publish-write`는 `ch{번호}_{챕터제목}.md` 형식으로 draft를 저장한다.
- `publish-export`는 outline 순서대로 대응 draft를 취합한다고 적어두지만, 정확히 어떤 규칙으로 매핑하는지가 스키마에 없다.

증거:
- `skills/shared/references/workspace-schema.md:192-207`
- `skills/publish-write/SKILL.md:193-209`
- `skills/publish-export/SKILL.md:100-118`

영향:
- 챕터 제목이 바뀌거나 유사 제목이 있으면 export가 틀린 파일을 집을 수 있다.
- 사람이 수동으로 고쳐야 하는 취약한 구조가 된다.

수정 제안:
- `outline` 항목에 `slug` 또는 `draft_file` 필드를 추가할 것.

예시:

```yaml
outline:
  - title: "1장: 로마서의 배경"
    slug: "ch01_background"
    draft_file: "ch01_background.md"
    status: done
```

- `publish-write`는 이 필드를 기준으로 저장
- `publish-export`는 이 필드를 기준으로 취합

대상 파일:
- `skills/shared/references/workspace-schema.md`
- `docs/specs/2026-04-21-publish-agent-design.md`
- `skills/publish-write/SKILL.md`
- `skills/publish-export/SKILL.md`

---

### 7. Codex/Gemini 호환 문구가 아직 검증 상태와 맞지 않음

심각도: 중간

문제:
- 상위 문서는 Codex/Gemini 호환처럼 읽힌다.
- 하지만 공통 문서는 도구 매핑이 `TBD`이며, 현재 검증 대상은 Claude Code라고 명시한다.
- 그런데 일부 스킬은 `WebFetch` 같은 Claude Code 도구명을 직접 적고 있다.

증거:
- `CLAUDE.md:50-51`
- `skills/shared/references/platform-tools.md:14-27`
- `skills/shared/references/platform-tools.md:208-212`
- `skills/publish-collect/SKILL.md:141`
- `skills/publish-collect/references/format-handling.md:121-125`

영향:
- 플랫폼 중립 문서라는 주장과 실제 스킬 문서가 모순된다.

수정 제안:
- 이번 단계에서 둘 중 하나를 선택할 것.

안 1:
- "현재 Claude Code 기준으로 검증됨"으로 내린다.

안 2:
- 각 플랫폼별 도구 대응을 실제로 채운다.

권장:
- 우선 안 1로 정리하고, Codex/Gemini 이식은 별도 작업으로 분리.

대상 파일:
- `CLAUDE.md`
- `skills/shared/references/platform-tools.md`
- `skills/publish-collect/SKILL.md`
- 기타 도구명 직접 표기한 스킬

---

## macOS / Windows 호환성 판정

### macOS

판정: 부분 지원

상태:
- `pandoc`, `file`, `iconv`, `shasum`은 보통 확보 가능
- PDF export는 `xelatex`와 한글 폰트가 추가로 필요
- PDF collect는 `pdftotext` 설치 안내가 부족함

의미:
- 약간의 의존성 정리만 하면 macOS는 현실적으로 운영 가능하다.

### Windows

판정: 현재 기준 미지원

이유:
- 설치 절차가 Unix 전용
- 경로 규칙이 Unix 전용
- `file`, `iconv`, `shasum`, `ln -sf`, `pdftotext` 등 기본 전제가 Windows 기본 환경과 맞지 않음
- PowerShell 또는 WSL 대응 절차가 없음

의미:
- 지금 상태에서 Windows 호환이라고 쓰면 안 된다.

### 권장 문구

현 시점 권장 표기:

> 현재 공식 지원 환경은 macOS/Linux이며, Windows는 아직 공식 지원하지 않습니다.
> Windows 지원이 필요하면 PowerShell 또는 WSL 기준 설치/실행 절차를 별도로 구현해야 합니다.

---

## Claude에게 제안하는 수정 순서

### 1단계: 문구와 범위 정리

- `CLAUDE.md`의 호환성 표기 수정
- `platform-tools.md`의 지원 범위 명확화
- Windows 미지원 또는 실험적 상태 명시

### 2단계: 깨지는 참조 경로 정리

- 설치 방식과 참조 방식 중 하나로 통일
- 실제 설치 후 reference 파일이 열리는지 기준으로 수정

### 3단계: collect/export의 허위 fallback 제거

- `pandoc -f pdf` 제거
- PDF 처리 의존성 안내 보강
- 포맷별 사전 점검 추가

### 4단계: 스키마 안정화

- `project.yaml outline`에 `slug` 또는 `draft_file` 추가
- write/export 간 파일 매핑을 명시적 계약으로 변경

### 5단계: 나중 작업으로 분리할 것

- Windows 지원
- Codex/Gemini 실제 이식
- OS별 셸 대체 명령 표 정교화

---

## 수정 완료 기준

Claude가 수정 후 아래 질문에 모두 "예"라고 답할 수 있어야 한다.

1. 설치 후 각 `SKILL.md`가 참조하는 문서를 실제로 열 수 있는가?
2. PDF collect에서 존재하지 않는 fallback를 더 이상 안내하지 않는가?
3. 현재 지원 OS/플랫폼 범위가 문서 전반에서 일관되는가?
4. macOS에서 필요한 추가 의존성이 모두 안내되는가?
5. Windows가 미지원이면 명확히 미지원으로 적혀 있는가?
6. `publish-write`가 만든 draft를 `publish-export`가 안정적으로 찾을 수 있는가?

---

## 짧은 결론

이 저장소는 설계 품질은 괜찮지만, "문서만 보면 되는 줄 알았는데 실제로는 안 되는" 지점이 몇 군데 있다.
이번 수정의 핵심은 기능 추가가 아니라 다음 세 가지다.

- 거짓 약속 제거
- 실제 설치/실행 경로 복구
- 지원 범위 명확화

Windows까지 진짜 지원하려면 별도 구현 작업으로 보는 것이 맞고, 이번 단계에서는 macOS/Linux 기준으로 문서를 정직하게 만드는 것이 우선이다.
