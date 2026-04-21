---
name: format-handling
description: publish-collect 스킬에서 사용하는 파일 형식별 변환 규칙, 인코딩 처리, content_hash 계산, raw entry 프론트매터 템플릿, 에러 처리 상세 가이드
---

# 파일 형식별 처리 규칙

`/publish-collect`가 각 파일 형식을 마크다운으로 변환하고 raw/entries/에 저장하기까지의 전체 처리 절차를 정의한다.

---

## 파일 형식별 변환

### 1. Markdown (`.md`)

**처리 방식:** 본문을 그대로 사용. 변환 없음.

**절차:**
1. 파일을 UTF-8로 읽는다.
2. 기존 YAML 프론트매터가 있으면 제거한다 (--- 블록 전체 삭제).
3. 정제된 본문 = 프론트매터 제거 후 나머지 전체.
4. publish-collect가 새 raw entry 프론트매터를 붙여 저장한다.

**주의:**
- 기존 프론트매터의 title 필드가 있으면 raw entry의 `title` 값으로 활용한다.
- 옵시디언 위키링크(`[[]]`)가 있으면 그대로 보존한다.

---

### 2. Plain Text (`.txt`)

**처리 방식:** 마크다운 본문으로 감싸기. 별도 포맷 변환 없음.

**절차:**
1. 인코딩 감지 실행 (아래 "인코딩 처리" 섹션 참조).
2. UTF-8로 변환된 텍스트를 읽는다.
3. 텍스트를 그대로 마크다운 본문으로 사용한다 (코드블록으로 감싸지 않음).
4. 제목 추론: 첫 번째 비어있지 않은 줄을 title로 사용. 없으면 파일명(확장자 제거).

**한국어 TXT 처리:**
- 줄바꿈이 `\r\n` (Windows)이면 `\n`으로 정규화한다.
- 연속된 빈 줄이 3개 이상이면 2개로 압축한다.

---

### 3. Word 문서 (`.docx`)

**처리 방식:** pandoc으로 마크다운 변환.

**필수 도구:** `pandoc` (미설치 시 해당 파일 건너뜀)

**변환 명령:**

```bash
pandoc -f docx -t markdown --wrap=none --extract-media="{workspace}/raw/media/" "{입력파일}" -o "{임시출력파일}.md"
```

**옵션 설명:**
- `-f docx`: 입력 형식 Word
- `-t markdown`: 출력 형식 마크다운
- `--wrap=none`: 줄바꿈 자동 삽입 금지 (긴 단락 보존)
- `--extract-media`: 삽입 이미지 추출 (이미지 경로 참조 유지)

**변환 후 정제:**
- pandoc이 생성하는 불필요한 메타 주석 (`<!-- -->`) 제거
- 빈 헤더(`## ` 뒤 내용 없음) 제거
- 표(table) 구조는 마크다운 표로 보존

**제목 추론:** 변환된 마크다운의 첫 번째 `#` 제목. 없으면 파일명.

---

### 4. PDF (`.pdf`)

**처리 방식:** 텍스트 추출. 이미지 전용 PDF는 미지원.

**우선 도구:** `pdftotext` (poppler-utils 패키지)

```bash
pdftotext -layout "{입력파일}" -
```

- `-layout`: 원본 레이아웃(컬럼 구조 등) 최대한 보존
- `-`: 표준 출력으로 결과 출력

**pdftotext 미설치 시:** 해당 PDF 파일을 건너뛰고 다음 경고를 출력한다.

```
[건너뜀] {파일명} — pdftotext가 설치되어 있지 않습니다.
PDF 수집을 위해 pdftotext를 설치해 주세요:
  macOS:   brew install poppler
  Ubuntu/Debian: sudo apt install poppler-utils
  Windows: choco install poppler
           또는 https://github.com/oschwartz10612/poppler-windows 에서 다운로드
```

pandoc은 PDF 입력 형식을 지원하지 않으므로 대체 도구로 사용하지 않는다.

**이미지 PDF 감지:**

pdftotext 출력이 다음 조건을 충족하면 이미지 PDF로 판정:
- 추출된 텍스트가 전체 페이지 대비 100자 미만
- 또는 추출된 텍스트가 빈 문자열

이미지 PDF 감지 시 처리:
```
해당 파일 건너뜀.
confidence: low로도 저장하지 않는다 (의미 있는 텍스트 없음).
리포트에 포함:
  [건너뜀] {파일명} — 스캔(이미지) PDF로 판정됨.
  텍스트를 추출할 수 없습니다.
  OCR 도구(예: Adobe Acrobat, Tesseract, ABBYY FineReader 등)로 텍스트를 인식한 뒤
  .txt 또는 .docx 파일로 저장하여 다시 수집해 주세요.
```

**PDF 변환 후 정제:**
- 페이지 구분자 (`\f`, Form Feed) → 마크다운 수평선(`---`) 또는 제거
- 머리글/바닥글로 보이는 반복 텍스트 제거 (페이지마다 동일한 짧은 줄)
- 불완전한 단어 하이픈 연결 (`단-\n어` → `단어`) 처리

**confidence 설정:**
- 텍스트 추출 성공, 구조 명확: `high`
- 일부 손실(표, 복잡한 레이아웃): `medium`
- 추출은 됐으나 많은 노이즈: `low`

---

### 5. 웹 URL

**처리 방식:** WebFetch로 가져온 후 마크다운 정제.

**절차:**
1. WebFetch 도구로 URL을 가져온다.
2. 반환된 내용(HTML 또는 이미 마크다운)에서 본문을 추출한다.
3. 마크다운 정제를 수행한다.

**마크다운 정제 규칙:**

제거 대상:
- 네비게이션 메뉴 (홈, 로그인, 구독 버튼 등)
- 광고 블록
- 댓글 섹션
- 소셜 공유 버튼 텍스트
- 헤더/푸터 반복 텍스트
- 관련 글 추천 섹션

보존 대상:
- 본문 제목 (첫 번째 `<h1>` 또는 `<h2>`)
- 본문 단락 전체
- 인용문 (`<blockquote>`)
- 코드 블록
- 인라인 링크 (URL은 제거하고 링크 텍스트만 보존 가능)
- 출판일, 저자 정보 (있을 경우)

**제목 추출:** `<title>` 태그 또는 첫 번째 `<h1>` 내용.

**한국 블로그 플랫폼 특이사항:**

| 플랫폼 | 특이사항 |
|--------|----------|
| 브런치 (brunch.co.kr) | WebFetch로 본문 추출 가능 |
| 티스토리 (tistory.com) | WebFetch로 대부분 가능 |
| 네이버 블로그 (blog.naver.com) | JavaScript 렌더링으로 내용 추출 불완전할 수 있음. 불완전 시 → confidence: low 또는 수동 복사 권장 |
| 워드프레스 | WebFetch로 본문 추출 가능 |
| 학술 DB (RISS, KISS 등) | 로그인 필요한 경우 추출 불가. 사용자에게 PDF 다운로드 후 재수집 권장 |

**confidence 설정:**
- 본문 추출 완전: `high`
- 일부 내용 누락 가능성: `medium`
- 네이버 블로그 등 불완전 추출: `low`

---

## 인코딩 처리

한국어 문서는 EUC-KR 또는 CP949(MS949) 인코딩으로 저장된 경우가 있다. 수집 전에 반드시 UTF-8로 변환한다.

### Windows 기본 인코딩

Windows에서 생성된 파일의 기본 인코딩은 로캘에 따라 다르다. 한국어 목사가 Windows에서 작성한 텍스트 파일은 CP949일 가능성이 높다.

| Windows 로캘 | 기본 인코딩 |
|-------------|-----------|
| 한국어 | CP949 |
| 일본어 | Shift_JIS |
| 중국어 (간체) | GBK |
| 서유럽 | CP1252 |

### UTF-8 BOM 처리

일부 Windows 편집기(메모장 등)는 UTF-8 파일 앞에 BOM(`0xEF 0xBB 0xBF`)을 삽입한다.

**BOM 감지 규칙:**
- 파일 첫 3바이트가 `0xEF 0xBB 0xBF`이면 UTF-8 BOM 파일이다.
- BOM 감지 시: BOM 바이트를 제거하고 나머지를 UTF-8로 처리한다.
- 처리 후 저장 시: 항상 **UTF-8 without BOM**으로 저장한다. BOM을 재삽입하지 않는다.

**Python으로 BOM 처리 (모든 OS 공통):**
```python
content = open('{입력파일}', 'rb').read()
if content.startswith(b'\xef\xbb\xbf'):
    content = content[3:]  # BOM 제거
text = content.decode('utf-8')
open('{출력파일}', 'w', encoding='utf-8').write(text)  # BOM 없이 저장
```

**또는 Python의 `utf-8-sig` 코덱 활용:**
```python
# utf-8-sig: 읽을 때 BOM 자동 제거, 쓸 때 BOM 없이 저장
text = open('{입력파일}', encoding='utf-8-sig').read()
open('{출력파일}', 'w', encoding='utf-8').write(text)
```

### 인코딩 감지

**macOS / Linux:**
```bash
file --mime-encoding "{파일경로}"
```

**Windows (PowerShell — chardet 라이브러리 사용):**
```powershell
python3 -c "import chardet; d=chardet.detect(open('{파일경로}','rb').read()); print(d['encoding'])"
```

(`chardet` 미설치 시: `pip install chardet`)

**출력 예 (macOS/Linux):**
```
document.txt: iso-8859-1
document.txt: utf-8
document.txt: unknown-8bit
```

**인코딩 판별표:**

| `file` 출력값 (macOS/Linux) | chardet 출력값 (Windows) | 실제 인코딩 | 처리 |
|-----------------------------|--------------------------|-------------|------|
| `utf-8` | `UTF-8` | UTF-8 | 변환 불필요 |
| `us-ascii` | `ascii` | ASCII (UTF-8 호환) | 변환 불필요 |
| `iso-8859-1` | `EUC-KR` / `CP949` | 한국어 파일이면 EUC-KR/CP949일 가능성 높음 | 변환 시도 |
| `unknown-8bit` | `EUC-KR` / `CP949` | EUC-KR/CP949일 가능성 높음 | 변환 시도 |
| `binary` | — | 바이너리 파일 | 처리 불가, 건너뜀 |

`file` 명령(macOS/Linux) 또는 chardet(Windows)가 없거나 결과가 불명확한 경우: config.yaml의 `defaults.encoding`을 따른다.

### UTF-8 변환 (EUC-KR/CP949 → UTF-8)

**macOS / Linux (iconv):**
```bash
iconv -f EUC-KR -t UTF-8 "{입력파일}" > "{임시파일}.utf8"
```

변환 실패 시 (iconv가 잘못된 문자 시퀀스 오류 반환):
```bash
iconv -f CP949 -t UTF-8 "{입력파일}" > "{임시파일}.utf8"
```

CP949도 실패 시:
```bash
iconv -f EUC-KR -t UTF-8//TRANSLIT "{입력파일}" > "{임시파일}.utf8"
```
(`//TRANSLIT`: 변환 불가 문자를 근사 문자로 대체. confidence를 `medium`으로 설정.)

**Windows (PowerShell — Python 사용):**
```powershell
python3 -c "
content = open('{입력파일}', encoding='euc-kr').read()
open('{임시파일}.utf8', 'w', encoding='utf-8').write(content)
"
```

EUC-KR 실패 시 CP949로 재시도:
```powershell
python3 -c "
content = open('{입력파일}', encoding='cp949').read()
open('{임시파일}.utf8', 'w', encoding='utf-8').write(content)
"
```

모든 시도 실패 시:
- 해당 파일 confidence: `low`
- 가능하면 Python fallback (모든 OS 공통):
  ```bash
  python3 -c "open('{출력}','w',encoding='utf-8').write(open('{입력}','rb').read().decode('cp949','replace'))"
  ```
- 그래도 실패: 건너뜀, 리포트에 포함

### config.yaml encoding 설정에 따른 동작

| `defaults.encoding` | 동작 |
|--------------------|------|
| `utf-8` | 감지 생략. 모든 파일을 UTF-8로 직접 읽음 |
| `euc-kr` | 감지 생략. 모든 파일을 EUC-KR로 읽고 UTF-8 변환 |
| `auto` | 항상 자동 감지 실행 (macOS/Linux: `file --mime-encoding`, Windows: chardet) |

### 경로 정규화 규칙

raw entry 프론트매터에 저장하는 `source_path`는 항상 슬래시(`/`) 구분자를 사용한다.

- Windows 경로 입력 예: `C:\Users\pastor\sermons\2026\설교문.txt`
- 저장 시 변환: `C:/Users/pastor/sermons/2026/설교문.txt`
- 모든 백슬래시(`\`)를 슬래시(`/`)로 변환한 뒤 프론트매터에 기록한다.

---

## content_hash 계산

중복 수집 방지를 위해 정제된 마크다운 본문의 SHA-256 해시를 계산한다.

### 해시 계산 대상

**포함:** 정제된 마크다운 본문 (프론트매터 제외)
**제외:** YAML 프론트매터, 수집 날짜, source_id 등 메타데이터

### 해시 계산 전 정규화

해시 계산 전에 본문을 다음과 같이 정규화한다 (표면적 차이로 인한 중복 누락 방지):

1. 줄바꿈을 `\n`으로 통일 (`\r\n` → `\n`)
2. 문자열 앞뒤 공백 제거 (`.strip()`)
3. 연속 빈 줄 압축 (3개 이상 → 2개)
4. 탭을 스페이스 4개로 변환

### 해시 계산 명령

**macOS:**
```bash
echo -n "{정규화된 본문}" | shasum -a 256 | awk '{print $1}'
```

**Linux:**
```bash
echo -n "{정규화된 본문}" | sha256sum | awk '{print $1}'
```

**Windows (PowerShell):**
```powershell
Get-FileHash -Algorithm SHA256 "{임시정규화파일}" | Select-Object -ExpandProperty Hash
```

또는 Python (모든 OS 공통 — 권장):
```bash
python3 -c "
import hashlib, sys
text = open('{임시정규화파일}', 'r', encoding='utf-8').read()
print('sha256:' + hashlib.sha256(text.encode('utf-8')).hexdigest())
"
```

### 저장 형식

```
sha256:a3f2c1d4e5b6f7890123456789abcdef0123456789abcdef0123456789abcdef01
```

### 중복 체크 절차

1. `raw/entries/` 내 모든 `.md` 파일을 Glob으로 목록화한다.
2. 각 파일의 프론트매터에서 `content_hash` 값을 읽는다.
3. 계산한 해시와 비교한다.
4. 일치하는 항목 발견 시: 중복 처리 (건너뜀).

---

## raw entry 프론트매터 전체 템플릿

스펙 4.2 기준. 모든 raw entry 파일 최상단에 이 프론트매터를 붙인다.

```yaml
---
source_id: src_{YYYYMMDD}_{N:03d}
batch_id: batch_{YYYYMMDD}
type: primary | reference
category: sermon | book | essay | commentary | thesis | article
title: "{추출 또는 추론된 제목}"
author: "{저자명}"
source_url: "{원본 URL, 로컬 파일이면 빈 문자열}"
source_path: "{로컬 파일 절대경로, 웹이면 빈 문자열}"
ingested_at: {YYYY-MM-DD}
confidence: high | medium | low
content_hash: "sha256:{64자리 해시}"
tags: []
absorbed: false
deleted: false
---
```

**각 필드 작성 지침:**

| 필드 | 작성 방법 |
|------|-----------|
| `source_id` | `src_{오늘날짜}_{순번3자리}`. 오늘 기준 기존 항목 최대 N 이후 부여 |
| `batch_id` | `batch_{오늘날짜}`. 오늘 수집 전체가 같은 batch_id |
| `type` | 사용자 지정 또는 config.yaml defaults.source_type |
| `category` | SKILL.md Step 3의 category 판별 기준표 참조 |
| `title` | 원문에서 추출. 없으면 파일명(확장자 제거)을 제목으로 |
| `author` | primary → config.yaml의 `author.name`. reference → 원문에서 추출. 불명확 시 빈 문자열 |
| `source_url` | 웹 URL 전체. 로컬 파일이면 `""` |
| `source_path` | 로컬 파일 절대경로. 웹 URL이면 `""` |
| `ingested_at` | 수집 실행 날짜 (YYYY-MM-DD) |
| `confidence` | format-handling.md 각 형식별 confidence 기준 참조 |
| `content_hash` | SHA-256 계산값 (위 섹션 참조) |
| `tags` | 초기값 `[]`. absorb 시 자동 채워짐 |
| `absorbed` | 항상 `false`로 시작. absorb 완료 시 `true`로 갱신 |
| `deleted` | 항상 `false`로 시작. soft delete 시 `true` |

---

## 에러 처리 상세

| 상황 | 감지 방법 | 대응 | confidence |
|------|-----------|------|------------|
| 손상된 DOCX | pandoc 비정상 종료 (exit code ≠ 0) | 건너뜀, 로그 기록 | — |
| 손상된 PDF | pdftotext 오류 또는 빈 출력 | 건너뜀, 로그 기록 | — |
| 이미지 PDF (스캔) | 추출 텍스트 100자 미만 | 건너뜀, OCR 안내 | — |
| 중복 content_hash | 기존 항목 해시 일치 | 건너뜀, 기존 source_id 안내 | — |
| 웹 내용 추출 실패 | WebFetch 오류 또는 빈 응답 | 건너뜀, 수동 입력 권장 | — |
| 인코딩 변환 실패 | iconv 오류 + Python fallback 실패 | 건너뜀, 로그 기록 | — |
| 인코딩 변환 부분 성공 | `//TRANSLIT` 사용 | 저장, 일부 문자 손실 경고 | `low` |
| pandoc 미설치 (DOCX) | `pandoc --version` 실패 | DOCX 파일 전체 건너뜀, 설치 안내 | — |
| pdftotext 미설치 | 명령 not found | 해당 PDF 파일 건너뜀, OS별 설치 안내 출력 | — |
| 네이버 블로그 불완전 추출 | 본문 길이 < 예상 대비 매우 짧음 | 저장하되 confidence: low, 수동 확인 권장 | `low` |
| HWP 파일 | `.hwp` 확장자 감지 | 건너뜀, DOCX 변환 안내 | — |
| config.yaml 없음 | 파일 읽기 실패 | 즉시 중단, /publish-setup 안내 | — |

**로그 파일 경로:** `{workspace}/logs/collect_{YYYYMMDD}.log`

**로그 항목 형식:**
```
[{YYYY-MM-DD HH:MM:SS}] [{상태}] {파일명 또는 URL} — {이유}
예:
[2026-04-22 14:30:15] [SKIP_DUPLICATE] 설교문_20250101.md — content_hash 일치: src_20260420_003
[2026-04-22 14:30:22] [ERROR] 강의록.pdf — pdftotext 오류: no text extracted (이미지 PDF 의심)
[2026-04-22 14:30:30] [SUCCESS] 로마서강해.docx → 20260422_src_20260422_001.md
```

---

## 형식별 처리 흐름 요약

```
입력 파일/URL
     │
     ├─ .md ──────→ 기존 프론트매터 제거 → 본문 추출
     │
     ├─ .txt ─────→ 인코딩 감지/변환 → 본문 그대로 사용
     │
     ├─ .docx ────→ pandoc 변환 → 마크다운 정제
     │
     ├─ .pdf ─────→ pdftotext (미설치 시 건너뜀) → 이미지PDF 감지 → 마크다운 정제
     │
     ├─ URL ──────→ WebFetch → HTML→마크다운 정제
     │
     └─ .hwp ─────→ 건너뜀 (안내)
          │
          ↓ (공통)
     인코딩 → UTF-8 정규화 (txt 외 형식도 결과 확인)
          │
          ↓
     content_hash 계산 (정규화된 본문 SHA-256)
          │
          ↓
     중복 체크 (raw/entries/ 스캔)
          │
     ┌────┴────┐
  중복 있음   없음
     │         │
  건너뜀    raw entry 저장
             ({YYYYMMDD}_{source_id}.md)
```

---

## 참조

- 스펙: `docs/specs/2026-04-21-publish-agent-design.md` — 섹션 4.2 (raw entry 포맷), 섹션 8 (지원 형식 + 에러 처리)
- 워크스페이스 구조: `shared/references/workspace-schema.md`
