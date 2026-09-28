---
name: publish-collect
description: Use when users say "/publish-collect", "자료 수집해줘", "이 파일들 분석해줘", "이 URL에서 가져와", "이 폴더 수집해줘", "원고 추가해줘", or want to add source materials (local files, directories, or web URLs) to the knowledge base
---

# Publish Collect — 자료 수집

로컬 파일 및 웹 URL에서 자료를 수집하여 `raw/entries/`에 정제된 마크다운으로 저장한다.
1차 자료(저자 본인 저작)와 2차 자료(외부 참고문헌)를 구분하여 태깅한다.

## 트리거 조건

```
한국어:
- "자료 수집해줘"
- "이 파일들 분석해줘" / "이 파일 넣어줘"
- "이 URL에서 가져와" / "이 링크 수집해줘"
- "이 폴더 수집해줘" / "이 디렉토리 처리해줘"
- "원고 추가해줘" / "설교문 추가해줘" / "책 파일 추가해줘"
- "새 자료 추가"

English:
- "/publish-collect"
- "/publish-collect [path or URL]"
- "collect this file/folder/URL"
- "add source material"
- "ingest these documents"
```

## 사전 조건

- `config.yaml`이 존재해야 한다. 없으면 즉시 중단하고 안내:
  ```
  config.yaml을 찾을 수 없습니다.
  먼저 /publish-setup으로 워크스페이스를 초기화해 주세요.
  ```

---

## 실행 절차

### Step 1: config.yaml 로드

워크스페이스의 `config.yaml`을 읽어 다음 값을 확인한다:

| 키 | 용도 |
|----|------|
| `workspace` (경로 기준) | raw/entries/ 저장 위치 |
| `author.id` | source_id 생성 시 참조 |
| `defaults.source_type` | 자료 유형 기본값 (`primary` 또는 `reference`) |
| `defaults.encoding` | 인코딩 기본값 (`utf-8`, `euc-kr`, `auto`) |
| `defaults.batch_size` | 이번 수집 세션 배치 ID 생성 참조 |

config.yaml 위치: 사용자가 명시하지 않으면 현재 작업 디렉토리 또는 이전에 확인된 워크스페이스 경로에서 찾는다.

### Step 2: 입력 분석

사용자가 제공한 입력을 파악한다.

**입력 유형 판별:**

| 입력 | 처리 |
|------|------|
| 단일 파일 경로 (`.md`, `.txt`, `.docx`, `.pdf`) | 해당 파일 1건 처리 |
| 디렉토리 경로 | 내부 지원 파일 전체 목록화 (재귀 탐색, 하위 폴더 포함) |
| 웹 URL (`http://`, `https://`) | WebFetch로 가져오기 |
| 복수 경로/URL (쉼표 또는 줄바꿈 구분) | 각각 처리 |

**자료 유형 확인 (primary / reference):**

- 사용자가 명시한 경우 → 그대로 사용
- 미지정 시 → `config.yaml`의 `defaults.source_type` 사용
- 불명확한 경우 사용자에게 질문:
  ```
  이 자료는 저자 본인의 글(primary)인가요, 외부 참고자료(reference)인가요?
  (기본값: primary)
  ```

**디렉토리 탐색 시 지원 확장자 필터:**
```
.md, .txt, .docx, .pdf
```
HWP 파일 발견 시 목록에서 제외하고 수집 후 안내 메시지에 포함.

**batch_id 생성:**
```
batch_{YYYYMMDD}
예: batch_20260422
```
같은 날 여러 번 수집할 경우 기존 batch_id를 재사용한다 (동일 날짜 기준).

### Step 3: 파일별 처리

각 파일/URL에 대해 순서대로 처리한다. 처리 실패 시 해당 항목을 건너뛰고 계속 진행한다.

**처리 순서:**

```
① 형식 감지
② 인코딩 감지 + UTF-8 정규화
③ 마크다운 변환
④ content_hash 계산
⑤ 중복 체크
⑥ raw entry 저장
```

#### ① 형식 감지

파일 확장자로 판별한다:

| 확장자 | 형식 |
|--------|------|
| `.md` | Markdown |
| `.txt` | Plain text |
| `.docx` | Word 문서 |
| `.pdf` | PDF |
| `.html`, `.htm` | HTML (웹 페이지) |
| URL | 웹 소스 |
| `.hwp` | **미지원** — 건너뜀 |
| 기타 | 건너뜀 |

#### ② 인코딩 감지 + UTF-8 정규화

→ `publish-collect/references/format-handling.md`의 "인코딩 처리" 섹션 참조 (표준 라이브러리 알고리즘 포함)
→ OS별 명령 참조: `shared/references/platform-tools.md` 8장, 9장

요약:
- 파일을 바이너리로 읽어 BOM → UTF-8 → CP949 → EUC-KR 순서로 디코딩을 시도한다 (표준 라이브러리만 사용, chardet 불필요)
- chardet 설치 시 더 정확한 감지 가능하나, 미설치 시에도 표준 라이브러리만으로 CP949/BOM 처리 가능
- config.yaml `defaults.encoding: utf-8` 이면 감지 생략하고 UTF-8로 처리
- `defaults.encoding: auto` 이면 항상 자동 감지 실행
- **Windows 환경 주의:** Windows 한국어 로캘의 기본 인코딩은 CP949이다. 인코딩이 명시되지 않은 파일은 CP949 가능성이 높다
- **UTF-8 BOM 처리:** 파일 시작에 BOM(`0xEF 0xBB 0xBF`)이 감지되면 제거 후 처리한다. 저장 시 항상 UTF-8 without BOM으로 저장한다
- **source_path 경로 정규화:** source_path에 백슬래시(`\`)가 포함된 경우(Windows 경로), 슬래시(`/`)로 변환하여 프론트매터에 저장한다

#### ③ 마크다운 변환

→ `publish-collect/references/format-handling.md`의 "파일 형식별 변환" 섹션 참조

형식별 변환 요약:
- `.md`: 기존 본문 그대로 사용
- `.txt`: 마크다운 코드블록 없이 본문으로 감싸기
- `.docx`: `pandoc -f docx -t markdown --wrap=none` 실행
- `.pdf`: `pdftotext -layout {파일} -` (pdftotext 미설치 시 해당 파일 건너뜀)
- 웹 URL: WebFetch → HTML → 마크다운 정제

변환 결과 = **정제된 마크다운 본문** (불필요한 메타데이터, 광고, 네비게이션 텍스트 제거)

#### ④ content_hash 계산

정제된 마크다운 본문(프론트매터 제외)의 SHA-256 해시를 계산한다 (OS별 명령은 `shared/references/platform-tools.md` 8장 참조).

형식: `sha256:{64자리 16진수}`
예: `sha256:a3f2c1d4e5b6...`

#### ⑤ 중복 체크

`raw/entries/` 디렉토리 내 모든 `.md` 파일의 프론트매터에서 `content_hash` 값을 읽어 비교한다.

- **일치하는 해시 있음:** 해당 파일을 건너뜀. 로그에 기록:
  ```
  [중복] {파일명} → 기존 항목: {source_id} ({기존파일명})
  ```
- **일치하는 해시 없음:** 새 항목으로 저장 진행

### Step 3.5: 대용량 파일 분할

파일 줄 수가 500줄을 초과하면 단일 entry로 저장하지 않고 분할 처리한다.

```
파일 줄 수 확인
  ↓
500줄 이하 → 단일 entry로 저장 (기존 흐름)
  ↓
500줄 이상 → 분할 처리:
  1. 파일 구조 스캔 (헤딩, 빈 줄 블록, 챕터 구분)
  2. 자연 분할점 기준으로 파트 분리
  3. 각 파트를 개별 entry로 저장
  4. 프론트매터에 parent_source_id, part, total_parts 추가
  5. 원본 전체 파일도 raw/entries/에 보관 (absorbed: false, is_parent: true)
```

**분할 기준 (형식별 자연 분할점):**

| 형식 | 분할점 |
|------|--------|
| Markdown | 헤딩 레벨 (# ## ###) |
| Plain text | 빈 줄 블록, 번호 매긴 섹션 |
| 설교 원고 | 서론/본론/결론/적용 마커 |
| 책 원고 | 장/절/챕터 마커 |

**분할 크기 기준:**

| 파일 크기 | 처리 방식 |
|----------|----------|
| 500줄 이하 | 그대로 단일 entry |
| 500-2000줄 | 자연 구분점 기준 2-5개 entry로 분할 |
| 2000줄 이상 | 반드시 분할, 각 파트 최대 500줄 |

Read 도구의 `offset`/`limit` 파라미터를 사용하여 청크 단위로 읽는다. 전체 파일을 한 번에 읽지 않는다.

→ 상세 규칙: `publish-collect/references/format-handling.md`의 "대용량 파일 분할 처리" 섹션 참조

---

#### ⑥ raw entry 저장

**파일명 규칙:**
```
{YYYYMMDD}_{source_id}.md
예: 20260422_src_20260422_001.md
```

`source_id` 생성:
```
src_{YYYYMMDD}_{N:03d}
예: src_20260422_001, src_20260422_002
```
N은 오늘 날짜 기준 이번 세션의 순번. 기존 항목과 겹치지 않도록 raw/entries/에서 최대 N을 확인한 뒤 이어서 부여.

**raw entry 프론트매터:**

```yaml
---
source_id: src_{YYYYMMDD}_{N:03d}
batch_id: batch_{YYYYMMDD}
type: primary | reference
category: sermon | book | essay | commentary | thesis | article
title: "{감지된 제목 또는 파일명에서 추론}"
author: "{저자명 — primary이면 config.yaml의 author.name, reference이면 원문에서 추출}"
source_url: "{웹 URL 또는 빈 문자열}"
source_path: "{로컬 파일 절대경로 또는 빈 문자열}"
ingested_at: {오늘 날짜 YYYY-MM-DD}
confidence: high | medium | low
content_hash: "sha256:{해시값}"
tags: []
absorbed: false
deleted: false
parent_source_id: ""    # 분할된 경우 원본 파일의 source_id, 분할 안 된 경우 빈 문자열
part: 0                 # 파트 번호 (0 = 분할 안 됨)
total_parts: 0          # 전체 파트 수 (0 = 분할 안 됨)
part_title: ""          # 파트 제목 (있으면)
---
```

**category 판별 기준:**

| category | 판별 신호 |
|----------|-----------|
| `sermon` | 파일명/제목에 설교, 강해, 주일, 수요 포함; 성경 본문 도입부 |
| `book` | 챕터 구조 (1장, Chapter 1 등), 목차 존재 |
| `essay` | 단편 에세이, 칼럼, 단독 글 |
| `commentary` | 성경 본문별 주석 구조 |
| `thesis` | 논문 형식 (초록, 참고문헌 등) |
| `article` | 블로그 글, 신문 기사, 기타 |

판별 불가 시 `article`로 기본 설정.

**confidence 판별 기준:**

| confidence | 기준 |
|------------|------|
| `high` | 텍스트 추출 완전, 구조 명확, 인코딩 정상 |
| `medium` | 일부 변환 손실 있음 (PDF 레이아웃 파손 등), 내용은 읽기 가능 |
| `low` | 상당한 손실 또는 추정 많음 (스캔 PDF 일부 텍스트 등) |

**본문 저장:**

프론트매터 아래에 정제된 마크다운 본문을 그대로 붙인다.

```markdown
---
{프론트매터}
---

{정제된 원문 내용}
```

### Step 4: 에러 처리

| 상황 | 대응 |
|------|------|
| 파일 변환 실패 (손상된 DOCX/PDF) | 해당 파일 건너뜀, 오류 로그 기록, 수집 리포트에 포함 |
| 중복 소스 감지 (content_hash 일치) | 기존 항목 source_id 안내, 새 수집 차단 |
| 웹 페이지 내용 추출 실패 | 수동 입력 권장 안내, 로그 기록 |
| HWP 파일 발견 | 건너뜀, 리포트에 "HWP → DOCX/TXT 변환 후 재시도 권장" 포함 |
| 이미지 PDF 감지 (텍스트 없음) | 건너뜀, "OCR 후 재입력" 안내 |
| 네이버블로그/JS 렌더링 URL 추출 불완전 | confidence: low로 저장, 또는 수동 복사 권장 |
| pandoc 미설치 (DOCX 변환 필요) | 해당 파일 건너뜀, "pandoc 설치 필요" 안내 |
| pdftotext 미설치 (PDF 변환 필요) | 해당 PDF 파일 건너뜀, 설치 안내 제공 (macOS: `brew install poppler` / Ubuntu: `sudo apt install poppler-utils` / Windows: `choco install poppler`) |
| 이미지 전용 PDF | 해당 파일 건너뜀, "OCR 처리 후 .txt 또는 .docx로 저장하여 재수집" 안내 |
| config.yaml 없음 | 즉시 중단, /publish-setup 안내 |

에러 로그는 `{workspace}/logs/collect_{YYYYMMDD}.log`에 저장한다.

### Step 5: 수집 리포트

모든 파일 처리 완료 후 다음 형식으로 보고한다:

```
수집 완료.

총 처리 대상: {입력된 파일/URL 수}건
  수집 성공: {N}건
  중복 건너뜀: {M}건
  실패/건너뜀: {K}건

형식별 분류:
  .md: {X}건
  .txt: {Y}건
  .docx: {Z}건
  .pdf: {W}건
  웹 URL: {V}건

자료 유형별:
  1차 자료 (primary): {A}건
  2차 자료 (reference): {B}건

저장 위치: {workspace}/raw/entries/
배치 ID: batch_{YYYYMMDD}
```

**HWP 발견 시 추가:**
```
⚠ HWP 파일 {N}건이 발견되었습니다.
  HWP는 지원되지 않습니다. 한글 워드프로세서에서 DOCX 또는 TXT로 저장 후 다시 수집해 주세요.
  파일 목록: {파일명 목록}
```

**실패 항목 있을 시 추가:**
```
처리 실패 항목:
  - {파일명}: {실패 이유}
  상세 로그: {workspace}/logs/collect_{YYYYMMDD}.log
```

**다음 단계 안내:**
```
수집이 완료되었습니다. 위키에 흡수할까요?
  → "위키 업데이트해줘" 또는 /publish-absorb 로 계속하세요.
```

---

## 1차 자료 vs 2차 자료 구분

| 구분 | 정의 | 예시 | absorbed 결과 |
|------|------|------|---------------|
| **primary** (1차 자료) | 저자 본인이 직접 쓴 원저작물 | 설교문, 저서 원고, 블로그 에세이, 칼럼, 기고문 | 저자 신학/문체 프로필 분석 대상 |
| **reference** (2차 자료) | 외부 참고자료 | 신학 논문, 주석서, 성경사전, 타 신학자 저서, 학술 자료 | KB 지식 보강용, 프로필 분석 제외 |

2차 자료는 `/publish-absorb`에서 `wiki/references/`에 흡수되며, `/publish-profile` 분석 대상에서 제외된다.

---

## 지원 형식 요약

| 형식 | 지원 | 비고 |
|------|------|------|
| Markdown (`.md`) | ✓ | 그대로 사용 |
| Plain text (`.txt`) | ✓ | 인코딩 감지 필요 |
| Word (`.docx`) | ✓ | pandoc 필요 |
| PDF (`.pdf`) | ✓ | 텍스트 기반만. 스캔 PDF는 OCR 후 재입력 |
| 웹 URL | ✓ | WebFetch 사용. JS 렌더링 사이트는 불완전할 수 있음 |
| HWP (`.hwp`) | ✗ | DOCX 또는 TXT로 변환 후 재입력 |
| 이미지 파일 | ✗ | 해당 없음 |

---

## 참조 문서

- `publish-collect/references/format-handling.md` — 파일 형식별 변환 규칙 + 인코딩 처리 + 에러 처리 상세 + 대용량 파일 분할 처리
- `shared/references/workspace-schema.md` — raw entry 프론트매터 스키마 + 워크스페이스 구조
- `shared/references/context-management.md` — 컨텍스트 윈도우 관리 전략 + 토큰 예산
