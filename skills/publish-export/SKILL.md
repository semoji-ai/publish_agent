---
name: publish-export
description: Use when users say "/publish-export", "PDF로 만들어줘", "출판용 파일", "ePub 변환", or want to convert drafts to publishable formats
---

# Publish Export — 출판용 파일 변환

프로젝트의 마크다운 초안을 pandoc으로 DOCX, PDF, ePub으로 변환하여 출판 가능한 파일을 생성한다.

## 트리거 조건

```
- "/publish-export"
- "PDF로 만들어줘"
- "출판용 파일 만들어줘"
- "ePub으로 변환해줘"
- "ePub 변환"
- "워드 파일로 내보내줘"
- "DOCX로 변환"
- "책 파일 만들어줘"
- "export해줘"
```

## 사전 조건

- config.yaml 존재 (publish-setup 완료)
- `projects/{project_name}/` 디렉토리 존재
- `projects/{project_name}/drafts/` 에 초안 파일 존재
- pandoc 설치 (DOCX, ePub, PDF 공통 필수. 미설치 시 Step 1에서 안내 후 중단)
- PDF 출력 시 추가 필요: xelatex, Noto Sans KR 폰트 (미설치 시 DOCX 내보내기 제안)

---

## WHEN TRIGGERED - EXECUTE IMMEDIATELY

### Step 1: 포맷별 의존성 확인

출력 포맷에 따라 필요한 도구가 다르다. 사용자가 원하는 포맷을 먼저 파악한 뒤(Step 2에서 확인), 해당 포맷에 필요한 의존성을 점검한다. 포맷 미정 상태에서는 pandoc 설치 여부만 먼저 확인한다.

**포맷별 필수 의존성:**

| 포맷 | 필수 도구 |
|------|-----------|
| DOCX | pandoc |
| ePub | pandoc |
| PDF  | pandoc + xelatex + Noto Sans KR 폰트 |

**pandoc 확인 (DOCX/ePub/PDF 공통):**

```bash
pandoc --version
```

pandoc 미설치 시 — 안내 후 중단:

```
pandoc이 설치되어 있지 않습니다. /publish-export를 사용하려면 pandoc이 필요합니다.

설치 방법:
  macOS:         brew install pandoc
  Ubuntu/Debian: sudo apt install pandoc
  Windows:       choco install pandoc
                 또는 winget install pandoc

설치 후 다시 시도하세요.
```

→ 여기서 중단. 이후 단계를 실행하지 않는다.

**PDF 추가 의존성 확인 (PDF 포맷 선택 시에만):**

xelatex 확인:
```bash
xelatex --version
```

Noto Sans KR 폰트 확인 (macOS):
```bash
fc-list | grep -i "Noto Sans KR"
```

Noto Sans KR 폰트 확인 (Linux):
```bash
fc-list | grep -i "Noto Sans CJK"
```

Noto Sans KR 폰트 확인 (Windows PowerShell):
```powershell
[System.Drawing.Text.InstalledFontCollection]::new().Families | Where-Object { $_.Name -like "*Noto Sans KR*" }
```

PDF 의존성 누락 시 — 즉시 실패하지 않고 대안을 제시한다:

```
PDF 생성에 필요한 도구가 설치되어 있지 않습니다.

누락된 항목:
  - xelatex: PDF 렌더링 엔진
  - Noto Sans KR: 한글 폰트

설치 방법:
  macOS:
    brew install --cask mactex-no-gui   # 전체 TeX 배포판 (~4GB)
    또는: brew install basictex && sudo tlmgr install xetex
    폰트: brew install --cask font-noto-sans-cjk-kr
  Ubuntu/Debian:
    sudo apt install texlive-xetex fonts-noto-cjk
  Windows:
    MiKTeX(https://miktex.org) 설치 — xelatex 포함 (choco install miktex 도 가능)
    Noto Sans KR 폰트: https://fonts.google.com/noto/specimen/Noto+Sans+KR 에서 다운로드 후 설치

지금 DOCX 또는 ePub으로 먼저 내보낼까요?
  → "예"라고 하면 DOCX로 내보냅니다.
  → 의존성 설치 후 다시 시도하면 PDF를 생성할 수 있습니다.
```

→ 사용자가 DOCX 대안을 수락하면 DOCX로 전환하여 Step 3~4를 진행한다.
→ 사용자가 거부하면 중단한다.

**pandoc 설치됨 + PDF 의존성 충족:** 버전을 확인하고 진행한다.

### Step 2: 대상 프로젝트 및 출력 포맷 확인

**프로젝트 확인:**

사용자가 프로젝트명을 지정하지 않은 경우, `projects/` 디렉토리의 프로젝트 목록을 보여주고 선택하게 한다:

```
어떤 프로젝트를 내보낼까요?
  1. 로마서 강해 (projects/로마서_강해/)
  2. 은혜의 교리 (projects/은혜의_교리/)
  3. ...
```

**출력 포맷 확인:**

사용자가 포맷을 지정하지 않은 경우:

```
출력 포맷을 선택하세요:
  1. DOCX — Microsoft Word 문서 (편집 가능)
  2. PDF  — 인쇄용 PDF (한글 폰트 필요)
  3. ePub — 전자책 (뷰어 호환)
```

여러 포맷을 동시에 선택할 수 있다.

### Step 3: 프로젝트 설정 및 초안 취합

`projects/{project_name}/project.yaml`을 읽어 프로젝트 정보를 로드한다.

**초안 취합 순서:**

`project.yaml`의 `outline` 배열 순서대로 `drafts/` 파일을 취합한다:

```yaml
# project.yaml 예시
outline:
  - title: "1장: 로마서의 배경"
    slug: "ch01_로마서의_배경"
    draft_file: "ch01_로마서의_배경.md"
    status: done
  - title: "2장: 의의 계시"
    slug: "ch02_의의_계시"
    draft_file: "ch02_의의_계시.md"
    status: done
```

- outline의 각 항목에서 `draft_file` 필드를 읽어 `drafts/{draft_file}` 경로의 파일을 순서대로 연결한다
- `draft_file` 필드가 없는 항목이 있으면 사용자에게 경고하고 해당 챕터를 건너뜀:
  ```
  경고: outline 항목 "{title}"에 draft_file 필드가 없습니다.
  해당 챕터를 건너뜁니다. project.yaml을 확인하거나 /publish-write를 다시 실행하세요.
  ```
- `draft_file`은 있지만 실제 파일이 `drafts/`에 존재하지 않는 경우 사용자에게 경고:
  ```
  경고: drafts/{draft_file} 파일을 찾을 수 없습니다.
  해당 챕터를 건너뜁니다. /publish-write로 해당 챕터 초안을 먼저 작성하세요.
  ```
- `status: done`이 아닌 항목이 있으면 사용자에게 경고:
  ```
  아직 완료되지 않은 챕터가 있습니다:
    - "3장: 율법과 복음" (status: pending)
  미완성 챕터를 포함하여 내보낼까요? (Y/N)
  ```
- outline이 없는 경우: `drafts/` 파일을 파일명 알파벳순으로 연결한다

**목차 및 표지 정보 구성:**

다음 정보를 pandoc 변환 시 사용한다:
- 제목: `project.yaml`의 `name`
- 저자: `config.yaml`의 `author.name`
- 날짜: 오늘 날짜

### Step 4: pandoc 변환 실행

출력 포맷별로 다음 명령을 실행한다.

**공통 준비:**

초안 파일들을 임시 연결 파일(`_export_combined.md`)로 합친 후 변환한다. 각 챕터 사이에 페이지 구분자(`\newpage`)를 삽입한다.

출력 디렉토리: `projects/{project_name}/exports/{format}/`
출력 파일명: `{project_name}_{YYYYMMDD}.{ext}`

**DOCX 변환:**

```bash
pandoc _export_combined.md \
  -f markdown \
  -t docx \
  --toc \
  --toc-depth=2 \
  --metadata title="{프로젝트명}" \
  --metadata author="{저자명}" \
  --metadata date="{오늘 날짜}" \
  -o projects/{project_name}/exports/docx/{파일명}.docx
```

**PDF 변환:**

```bash
pandoc _export_combined.md \
  -f markdown \
  -t pdf \
  --pdf-engine=xelatex \
  --variable mainfont="Noto Sans KR" \
  --variable fontsize=11pt \
  --variable geometry="a4paper, margin=2.5cm" \
  --toc \
  --toc-depth=2 \
  --metadata title="{프로젝트명}" \
  --metadata author="{저자명}" \
  --metadata date="{오늘 날짜}" \
  -o projects/{project_name}/exports/pdf/{파일명}.pdf
```

**PDF 관련 오류 처리:**

xelatex 미설치 오류 발생 시:
```
PDF 생성에 실패했습니다. xelatex이 필요합니다.
  macOS:  brew install --cask mactex
  Linux:  sudo apt install texlive-xetex

Noto Sans KR 폰트 미설치 오류 발생 시:
  macOS:  brew install --cask font-noto-sans-cjk-kr
  Linux:  sudo apt install fonts-noto-cjk

폰트 설치 후 다시 시도하거나, DOCX 또는 ePub 포맷을 먼저 사용하세요.
```

**ePub 변환:**

```bash
pandoc _export_combined.md \
  -f markdown \
  -t epub \
  --toc \
  --toc-depth=2 \
  --metadata title="{프로젝트명}" \
  --metadata author="{저자명}" \
  --metadata date="{오늘 날짜}" \
  -o projects/{project_name}/exports/epub/{파일명}.epub
```

### Step 5: 완료 리포트

변환이 완료된 후 사용자에게 보고한다:

```
내보내기 완료.

프로젝트: {프로젝트명}
저자: {저자명}

생성된 파일:
  DOCX: projects/{project_name}/exports/docx/{파일명}.docx ({파일크기})
  PDF:  projects/{project_name}/exports/pdf/{파일명}.pdf ({파일크기})
  ePub: projects/{project_name}/exports/epub/{파일명}.epub ({파일크기})

포함된 챕터: {N}개
총 {M}페이지 (PDF 기준 추정)
```

변환 실패 포맷이 있으면:
```
실패한 포맷:
  PDF: xelatex 미설치로 실패 (위 설치 안내 참조)
```

---

## 주의 사항

- **한글 PDF:** xelatex 엔진과 Noto Sans KR 폰트가 모두 설치되어야 한다. 둘 중 하나라도 없으면 PDF 생성이 실패한다.
- **대용량 원고:** pandoc 변환은 원고 분량에 따라 시간이 걸릴 수 있다. 특히 PDF(xelatex)는 수 분이 소요될 수 있다.
- **이미지:** 초안에 이미지가 포함된 경우, 이미지 파일이 `drafts/` 상대 경로 기준으로 존재해야 한다.
- **재실행:** 같은 포맷으로 다시 내보내면 기존 파일을 덮어쓴다. 이전 파일이 필요하면 날짜가 다른 파일명으로 보관한다.

---

## 참조 문서

- `shared/references/workspace-schema.md` — project.yaml 스키마, 디렉토리 구조
