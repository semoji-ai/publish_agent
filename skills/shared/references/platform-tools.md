---
name: platform-tools
description: Publish Agent 스킬의 플랫폼별 도구 매핑 가이드. Claude Code(확정), Codex(TBD), Gemini CLI(TBD) 간 도구 대응 관계, Agent 비호환 대응, 플랫폼 중립적 스킬 작성 규칙.
---

# 플랫폼 도구 매핑 가이드

> **검증 상태:** 현재 **Claude Code만 실제로 검증됨**. Codex(OpenAI)와 Gemini CLI는 도구 매핑이 정의되어 있으나 아직 테스트되지 않음(TBD). 각 플랫폼 포팅 시 6장 체크리스트로 실제 동작을 확인해야 한다.

Publish Agent 스킬은 Claude Code 기준으로 개발·검증되었으며, Codex(OpenAI)·Gemini CLI로의 이식을 염두에 둔 플랫폼 중립적 설계를 따른다. 이 문서는 각 플랫폼에서 동일한 작업을 수행하는 도구들 간의 매핑 관계를 정의한다.

---

## 1. 도구 매핑 테이블

| 기능 | Claude Code | Codex (TBD) | Gemini CLI (TBD) |
|------|-------------|-------------|-------------------|
| 파일 읽기 | `Read` | TBD | TBD |
| 파일 쓰기 (신규/전체 덮어쓰기) | `Write` | TBD | TBD |
| 파일 편집 (부분 수정) | `Edit` | TBD | TBD |
| 파일 검색 (패턴/glob) | `Glob` | TBD | TBD |
| 내용 검색 (regex) | `Grep` | TBD | TBD |
| 셸 명령 실행 | `Bash` | TBD | TBD |
| 웹 페이지 가져오기 | `WebFetch` | TBD | TBD |
| 병렬 서브에이전트 | `Agent` | **미지원** | **미지원** |

**TBD 항목 처리 방침:**
- Codex와 Gemini CLI의 구체적인 도구명은 각 플랫폼 공식 문서 기반으로 구현 시 확인 필요
- 스킬 파일(SKILL.md)에서는 도구명 대신 **행위 중심 기술**을 사용하여 플랫폼 중립성 유지 (아래 5장 참조)

---

## 2. Agent 도구 비호환 대응

### 상황 설명

Claude Code의 `Agent` 도구는 병렬 서브에이전트를 실행한다. Codex와 Gemini CLI에는 이에 대응하는 기능이 없다.

**영향을 받는 워크플로우:**
- `/publish-absorb`: 다수의 항목을 병렬 처리하여 속도 향상 가능
- `/publish-profile`: 4개 분석 차원을 병렬로 분석 가능
- `/publish-review`: 4차원 심사를 병렬로 수행 가능

### 대응 패턴: 조건부 병렬 처리

SKILL.md에서 병렬 처리가 가능한 부분은 다음과 같이 조건부로 기술한다:

```markdown
### Step N: {작업명}

다음 분석을 수행한다 (가능한 경우 병렬로, 아니면 순차적으로):

1. {분석 항목 A}
2. {분석 항목 B}
3. {분석 항목 C}
```

### 순차 처리 구현 원칙

병렬 처리가 불가한 플랫폼에서는 동일한 작업을 순차적으로 실행한다:

```
병렬 처리 (Claude Code):
  Agent 1: A 분석
  Agent 2: B 분석       ← 동시 실행
  Agent 3: C 분석

순차 처리 (Codex / Gemini CLI):
  Step 1: A 분석
  Step 2: B 분석        ← 순서대로 실행
  Step 3: C 분석
```

결과물은 동일하며, 처리 시간만 차이가 난다. 순차 처리 시 체크포인트를 더 자주 저장하여 중단 시 재개 가능하도록 설계한다.

---

## 3. 플랫폼별 주요 차이

### 파일 경로 처리

| 항목 | Claude Code | 비고 |
|------|-------------|------|
| 절대 경로 | 지원 | macOS/Linux: `/Users/...`, Windows: `C:\Users\...` |
| 상대 경로 | 지원 | cwd 기준 |
| 경로 구분자 | `/` (macOS/Linux), `\` (Windows) | Windows에서는 PowerShell이 `/`도 허용하는 경우 많음 |

### 셸 명령 실행 (`Bash`)

Claude Code의 `Bash` 도구:
- macOS/Linux 셸 명령 실행
- 타임아웃 설정 가능
- 백그라운드 실행 가능

Codex/Gemini CLI 대응:
- 각 플랫폼의 셸 실행 기능 사용 (TBD)
- 셸 의존 명령(예: `pandoc`, `iconv`, `sha256sum`)은 해당 명령이 설치되어 있어야 함

### pandoc 연동 (`/publish-export`)

pandoc은 외부 CLI 도구이므로 플랫폼 무관하게 동일하게 호출된다:

```bash
pandoc -f markdown -t docx --toc input.md -o output.docx
pandoc -f markdown -t pdf --pdf-engine=xelatex input.md -o output.pdf
pandoc -f markdown -t epub --toc input.md -o output.epub
```

단, 셸 실행 도구의 이름/인터페이스가 플랫폼마다 다를 수 있음.

### WebFetch 동작 차이

한국 블로그 플랫폼(네이버블로그, 브런치 등)은 JavaScript 렌더링으로 인해 WebFetch로 내용 추출이 불완전할 수 있다. 이 경우:
1. 사용자에게 수동 복사 후 `.md`/`.txt` 로컬 저장 요청
2. 로컬 파일로 재수집

---

## 4. 플랫폼 감지

스킬 실행 중 현재 플랫폼을 명시적으로 감지할 필요는 없다. 대신:
- 병렬 처리가 가능하면 활용
- 가능하지 않으면 순차 처리로 폴백
- 사용 가능한 도구로 동일한 결과를 달성

---

## 5. 플랫폼 중립적 SKILL.md 작성 가이드

### 원칙: 행위(action) 중심으로 기술

SKILL.md는 **무엇을 해야 하는가**를 기술하며, 특정 도구 이름에 의존하지 않는다.

#### 권장 표현 (플랫폼 중립)

```markdown
## Step 3: config.yaml 로드

워크스페이스 루트의 config.yaml을 읽어 설정 값을 로드한다.
- 읽어야 할 필드: workspace.name, author.id, defaults.batch_size
- 파일이 없으면 오류 처리: "config.yaml을 찾을 수 없습니다. /publish-setup을 먼저 실행하세요."
```

#### 지양하는 표현 (플랫폼 종속)

```markdown
## Step 3: config.yaml 로드

Read 도구로 {workspace}/config.yaml을 읽는다.
```

### 예외: Claude Code 특화 섹션

일부 스킬은 Claude Code의 고급 기능을 활용하는 섹션을 별도로 표기할 수 있다:

```markdown
#### (Claude Code 한정) 병렬 분석

Claude Code 환경에서는 Agent 도구를 사용하여 4가지 분석을 동시에 실행한다.
다른 플랫폼에서는 아래 순차 처리 섹션을 따른다.

#### 순차 분석 (모든 플랫폼)

1. 문체 분석 → style.yaml 작성
2. 신학 분석 → theology.yaml 작성
3. 설교 구조 분석 → sermon_pattern.yaml 작성
4. 어휘 분석 → vocabulary.md 작성
```

### 파일 경로 표기 규칙

SKILL.md 내 경로는 워크스페이스 루트(`{workspace}`)를 기준으로 한다:

```markdown
# 권장: 변수 기반 표기
{workspace}/wiki/_index.md
{workspace}/raw/entries/

# 스킬 자체 참조 파일: 상대 경로
shared/references/workspace-schema.md
publish-absorb/references/absorb-prompt.md
```

실행 시 `{workspace}` 값은 `config.yaml`의 `workspace` 설정에서 읽어온다.

---

## 6. 구현 검증 체크리스트

새 플랫폼(Codex, Gemini CLI)에 스킬을 포팅할 때 확인할 사항:

```
[ ] 파일 읽기/쓰기/편집 도구 매핑 확인
[ ] Glob/Grep 대응 도구 확인 (파일 패턴 검색, 내용 검색)
[ ] Bash 대응 셸 실행 도구 확인
[ ] WebFetch 대응 웹 요청 도구 확인
[ ] Agent 미지원 → 순차 처리 패턴 적용 확인
[ ] pandoc 호출 가능 여부 확인
[ ] 파일 인코딩 처리 (utf-8 기본, euc-kr 변환) 동작 확인
[ ] 체크포인트 저장 (_absorb_log.json 쓰기) 동작 확인
[ ] SHA-256 해시 계산 방법 확인 (Bash 의존 또는 대안)
```

---

## 7. 현재 지원 플랫폼 상태

| 플랫폼 | 상태 | 비고 |
|--------|------|------|
| Claude Code | 확정 지원 | 모든 도구 사용 가능. Agent 병렬 처리 활용 가능 |
| Codex (OpenAI) | 미확인 (TBD) | 구현 시 공식 API 문서 기반 도구 매핑 필요 |
| Gemini CLI | 미확인 (TBD) | 구현 시 공식 API 문서 기반 도구 매핑 필요 |

**현재 개발 및 검증 대상: Claude Code**

---

## 8. OS별 셸 명령 매핑

스킬에서 셸 명령이 필요한 경우, 아래 표를 참조하여 OS에 맞는 명령을 사용한다.

**원칙: SKILL.md는 행위를 기술하고, 구체적인 명령은 이 표를 참조한다.**

| 작업 | macOS | Linux | Windows (PowerShell) |
|------|-------|-------|----------------------|
| 인코딩 감지 | `file --mime-encoding {파일}` | `file --mime-encoding {파일}` | Python: `import chardet; chardet.detect(open(f,'rb').read())` |
| 인코딩 변환 (EUC-KR → UTF-8) | `iconv -f EUC-KR -t UTF-8 {입력} > {출력}` | `iconv -f EUC-KR -t UTF-8 {입력} > {출력}` | Python: `open(f, encoding='euc-kr').read()` → `open(out,'w',encoding='utf-8').write(...)` |
| SHA-256 해시 계산 | `shasum -a 256 {파일}` | `sha256sum {파일}` | `Get-FileHash -Algorithm SHA256 {파일}` |
| PDF 텍스트 추출 | `pdftotext` (설치: `brew install poppler`) | `pdftotext` (설치: `sudo apt install poppler-utils`) | `pdftotext` (설치: `choco install poppler`) |
| DOCX → 마크다운 변환 | `pandoc -f docx -t markdown` | `pandoc -f docx -t markdown` | `pandoc -f docx -t markdown` (동일) |
| 심볼릭 링크 생성 | `ln -sf {대상} {링크}` | `ln -sf {대상} {링크}` | `New-Item -ItemType Junction -Path {링크} -Target {대상}` |
| 디렉토리 목록 조회 | `ls` | `ls` | `Get-ChildItem` |

### Windows 사용 시 참고

- **Python 활용 권장:** 인코딩 감지(`chardet`)와 변환은 Python으로 처리하는 것이 가장 안정적이다. Python 3는 Windows에서도 기본 제공되거나 쉽게 설치 가능하다.
- **PowerShell 실행 정책:** 스크립트 실행 시 `Set-ExecutionPolicy RemoteSigned` 설정이 필요할 수 있다.
- **경로 구분자:** PowerShell은 `/`도 대부분 허용하지만, 네이티브 명령에서는 `\`를 사용한다.
- **pandoc, pdftotext:** Windows에서는 Chocolatey(`choco`) 또는 winget으로 설치한다. 설치 후 PATH 재설정이 필요할 수 있다.
