---
name: publish-setup
description: Use when users say "/publish-setup", "워크스페이스 만들어줘", "publish agent 설정", "출판 에이전트 시작", or when this is the first use of publish agent skills
---

# Publish Setup — 워크스페이스 초기화

새로운 Publish Agent 워크스페이스를 생성하고 저자 프로필 디렉토리를 초기화한다.

## 트리거 조건

```
- "/publish-setup"
- "/publish-setup [경로]"
- "워크스페이스 만들어줘"
- "publish agent 설정"
- "출판 에이전트 시작"
- "출판 에이전트 설정해줘"
- publish agent 스킬 최초 사용 감지 시 (config.yaml 미존재)
```

## 사전 조건

없음. 이 스킬이 모든 것의 시작점이다.

---

## 실행 절차

### Step 1: 사용자 정보 수집

사용자에게 대화형으로 질문한다. 최소 정보만 필수, 나머지는 선택.

**필수:**
1. 워크스페이스 경로 — 기본값 제안: `~/publish_workspace/`
2. 저자 이름

**선택:**
3. 교단 (예: 대한예수교장로회, 기독교대한감리회 등)
4. 직분 (예: 담임목사, 부목사, 강도사, 신학교수 등)

저자 이름에서 `author_id`를 자동 생성한다:
- 한글: 성_이름 로마자 변환 또는 한글 그대로 (예: "김철수" → `kim_cheolsu` 또는 `김철수`)
- 영문: 소문자 + 언더스코어 (예: "John Smith" → `john_smith`)
- 사용자가 직접 지정할 수도 있음

### Step 2: 의존성 확인

시스템 환경과 도구 설치 상태를 점검한다.

#### 2a: OS 감지
- 실행 환경이 macOS/Linux/Windows인지 판별

#### 2b: 기본 필수 도구

| 도구 | 확인 명령 | 용도 |
|------|----------|------|
| pandoc | `pandoc --version` | 파일 변환 + export |
| Python (Windows만) | `py -3 --version` | 인코딩 처리 |

#### 2c: 선택 기능 도구

| 도구 | 확인 명령 | 용도 | 미설치 시 |
|------|----------|------|----------|
| pdftotext | `pdftotext -v` | PDF 수집 | PDF 수집 불가 |
| xelatex | `xelatex --version` | PDF export | PDF export 불가 |
| Noto Sans KR | (폰트 확인) | 한글 PDF | 한글 PDF 불가 |

#### 2d: 점검 결과 리포트

```text
환경 점검 결과 (Windows)

필수 도구:
  [OK] pandoc v3.1
  [OK] Python 3.12 (py -3)

선택 도구:
  [OK] pdftotext v24.04
  [MISSING] xelatex → PDF export 불가 (설치: choco install miktex)
  [MISSING] Noto Sans KR → 한글 PDF 불가 (설치: https://fonts.google.com/noto/specimen/Noto+Sans+KR)

현재 가능한 기능:
  - 텍스트/DOCX/PDF 수집
  - 위키 구축 및 집필
  - DOCX/ePub export

현재 불가능한 기능:
  - PDF export (xelatex + Noto Sans KR 설치 필요)
```

**필수 도구 실패 처리 규칙:**

| 상황 | 동작 | 영향 |
|------|------|------|
| pandoc 없음 | 경고 후 계속 | collect 일부 가능 (md/txt만), export 전체 불가 |
| Windows에서 `py -3` 없음 | 경고 후 계속 | 인코딩 자동 감지 불가, CP949 텍스트 수집 실패 가능 |
| pdftotext 없음 | 안내 후 계속 | PDF 수집 불가 |
| xelatex 없음 | 안내 후 계속 | PDF export 불가 |
| Noto Sans KR 없음 | 안내 후 계속 | 한글 PDF export 불가 |

- setup 자체는 어떤 도구가 없어도 **중단하지 않는다** (워크스페이스 생성은 항상 완료)
- 완료 리포트에서 "가능한 기능 / 제한된 기능"을 명확히 분리하여 표시

### Step 3: 디렉토리 구조 생성

**Windows 경로 처리:** 사용자가 워크스페이스 경로를 백슬래시(`\`)로 입력한 경우, 슬래시(`/`)로 변환한 뒤 저장한다. config.yaml에 저장되는 모든 경로는 `/` 구분자를 사용한다.
- 입력 예: `C:\Users\pastor\publish_workspace`
- 저장 값: `C:/Users/pastor/publish_workspace`

워크스페이스 경로에 다음 구조를 생성한다:

```
{workspace}/
├── authors/{author_id}/
├── wiki/
│   ├── people/
│   ├── concepts/
│   ├── sermons/
│   ├── books/
│   ├── passages/
│   └── references/
├── raw/
│   └── entries/
├── plans/
├── projects/
├── snapshots/
└── logs/
```

### Step 4: 초기 파일 생성

#### 4a: config.yaml

```yaml
workspace:
  name: "{사용자 입력 또는 저자명 + 서재}"
  created: {오늘 날짜 YYYY-MM-DD}
  version: 1

author:
  id: "{author_id}"
  name: "{저자 이름}"
  denomination: "{교단 — 미입력 시 빈 문자열}"
  role: "{직분 — 미입력 시 빈 문자열}"

defaults:
  source_type: primary
  batch_size: 15
  review_max_rounds: 3
  encoding: auto                   # Windows: auto (CP949 자동 감지), macOS/Linux: utf-8도 가능

export:
  pandoc_path: "{pandoc 경로 또는 pandoc}"
```

#### 4b: 저자 프로필 빈 파일

`authors/{author_id}/` 아래 4개 파일 생성:

**theology.yaml:**
```yaml
# 신학적 입장 — /publish-profile 실행 시 자동 채워짐
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
```

**style.yaml:**
```yaml
# 문체 프로필 — /publish-profile 실행 시 자동 채워짐
tone: ""
sentence_length: ""
rhetoric:
  metaphor_frequency: ""
  favorite_metaphors: []
argumentation: ""
paragraph_style: ""
```

**sermon_pattern.yaml:**
```yaml
# 설교 구조 패턴 — /publish-profile 실행 시 자동 채워짐
structure: ""
intro_ratio: 0
body_ratio: 0
application_ratio: 0
illustration_frequency: ""
scripture_citation_style: ""
```

**vocabulary.md:**
```markdown
# 어휘 패턴

> /publish-profile 실행 시 자동 채워짐

## 자주 쓰는 표현

(분석 전)

## 피하는 표현

(분석 전)

## 성경 인용 방식

- 번역본:
- 인용 형식:
```

#### 4c: 위키 인덱스 파일

**wiki/_index.md:**
```markdown
# Wiki Index

> 아직 기사가 없습니다. /publish-collect로 자료를 수집한 후 /publish-absorb로 위키를 구축하세요.
```

**wiki/{category}/_index.md** (people, concepts, sermons, books, passages, references 각각):
```markdown
# {Category} Index

(아직 기사가 없습니다)
```

**wiki/_backlinks.json:**
```json
{}
```

**wiki/_absorb_log.json:**
```json
{
  "batches": [],
  "pending_entries": []
}
```

### Step 5: 완료 리포트

사용자에게 다음을 보고한다:

```
워크스페이스가 준비되었습니다.

경로: {workspace 경로}
저자: {저자 이름} ({author_id})
생성된 디렉토리: {N}개
생성된 파일: {M}개

환경 점검 결과:
  필수 도구:
    {pandoc: [OK] v{버전} / [MISSING] → export 불가}
    {Python (Windows): [OK] v{버전} / [MISSING] → 인코딩 처리 불가}
  선택 도구:
    {pdftotext: [OK] / [MISSING] → PDF 수집 불가}
    {xelatex: [OK] / [MISSING] → PDF export 불가}
    {Noto Sans KR: [OK] / [MISSING] → 한글 PDF 불가}

다음 단계:
기존 설교문, 저서, 글 등이 있는 폴더 경로나 URL을 알려주세요.
자료를 수집하여 나만의 신학 위키를 구축합니다.
```

---

## 참조 문서

- `shared/references/workspace-schema.md` — 워크스페이스 구조 + 전체 스키마
- `shared/references/author-profile-schema.md` — 저자 프로필 4파일 스키마
