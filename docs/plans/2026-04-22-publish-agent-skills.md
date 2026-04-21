# Publish Agent Skills Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create 9 LLM skills that build a personal theological wiki from an author's writings and use it for book authoring, revision, and sermon preparation.

**Architecture:** Each skill is a SKILL.md file (Claude Code/Codex/Gemini CLI compatible) with supporting references and templates. Skills share a common workspace structure (obsidian vault + LLM wiki hybrid) and author profile system. No code — pure prompt/workflow definitions.

**Tech Stack:** Markdown skills (SKILL.md), YAML schemas, pandoc (export only)

**Spec:** `docs/specs/2026-04-21-publish-agent-design.md`

---

## File Structure

All skills live under `/Users/hannah/Projects/publish_agent/skills/`:

```
skills/
├── shared/                              # 공유 리소스
│   └── references/
│       ├── workspace-schema.md          # 워크스페이스 구조 + 모든 YAML/JSON 스키마
│       ├── wiki-article-format.md       # 2-tier 기사 포맷 + 위키링크 규칙
│       ├── author-profile-schema.md     # 저자 프로필 4파일 스키마
│       ├── platform-tools.md            # Claude Code/Codex/Gemini 도구 매핑
│       ├── absorb-rules.md             # 흡수 매칭/분리/병합 로직
│       └── search-strategy.md           # 계층적 요약 검색 전략
├── publish-setup/
│   └── SKILL.md
├── publish-collect/
│   ├── SKILL.md
│   └── references/
│       └── format-handling.md           # 파일 형식별 변환 규칙 + 에러 처리
├── publish-absorb/
│   ├── SKILL.md
│   └── references/
│       └── absorb-prompt.md             # 흡수용 LLM 프롬프트 템플릿
├── publish-profile/
│   ├── SKILL.md
│   └── references/
│       └── analysis-dimensions.md       # 문체/신학/설교구조/어휘 분석 기준
├── publish-write/
│   ├── SKILL.md
│   └── references/
│       └── writing-modes.md             # 신규/개정/설교집/강해서 모드별 가이드
├── publish-review/
│   ├── SKILL.md
│   └── references/
│       └── review-rubric.md             # 4차원 심사 기준표
├── publish-curate/
│   └── SKILL.md
├── publish-export/
│   └── SKILL.md
└── publish-sermon/
    └── SKILL.md
```

---

## Chunk 1: 공유 리소스 + publish-setup

이 청크에서 모든 스킬이 참조할 공유 문서를 만들고, 워크스페이스를 초기화하는 첫 번째 스킬을 작성한다.

### Task 1: shared/references/workspace-schema.md

**Files:**
- Create: `skills/shared/references/workspace-schema.md`

- [ ] **Step 1: 워크스페이스 디렉토리 구조 문서 작성**

스펙 섹션 4의 전체 디렉토리 트리를 포함하되, 각 디렉토리/파일의 용도를 한줄씩 설명. config.yaml, project.yaml, _absorb_log.json, _backlinks.json, manifest.json의 전체 스키마를 코드블록으로 포함.

```markdown
---
name: workspace-schema
description: Publish Agent 워크스페이스 구조 및 전체 YAML/JSON 스키마 정의
---

# 워크스페이스 구조

## 디렉토리 트리
{스펙 섹션 4의 트리 — 각 항목에 한줄 설명}

## config.yaml
{스펙 4.0 스키마 전체}

## project.yaml
{스펙 4.6 스키마 전체}

## _absorb_log.json
{스펙 4.5 스키마 전체}

## _backlinks.json
{스펙 4.4 스키마 전체}

## snapshots/manifest.json
{스펙 4.7 스키마 전체}
```

- [ ] **Step 2: 검증**

파일 읽어서 스펙의 모든 스키마(4.0, 4.4, 4.5, 4.6, 4.7)가 빠짐없이 포함되었는지 확인.

### Task 2: shared/references/wiki-article-format.md

**Files:**
- Create: `skills/shared/references/wiki-article-format.md`

- [ ] **Step 1: 위키 기사 포맷 문서 작성**

스펙 4.1의 2-tier 구조, index.md 프론트매터 스키마, 요약 블록 형식, chunks/ 규칙, 카테고리 _index.md 예시를 포함.

포함할 내용:
- 2-tier 디렉토리 구조 (`{article}/index.md` + `chunks/`)
- index.md YAML 프론트매터 전체 필드 (title, type, created, updated, summary, related, sources, tags, chunk_count)
- 요약 블록 형식 (`> **요약:** ...`)
- 위키링크 규칙 (`[[기사명]]` — 옵시디언 호환)
- 카테고리 _index.md 포맷 (제목 + 한줄 요약 목록)
- Anti-cramming/Anti-thinning 기준 (200줄/15줄)

- [ ] **Step 2: 검증**

### Task 3: shared/references/author-profile-schema.md

**Files:**
- Create: `skills/shared/references/author-profile-schema.md`

- [ ] **Step 1: 저자 프로필 스키마 문서 작성**

4개 프로필 파일의 구조를 정의:

```yaml
# theology.yaml 예시
soteriology:           # 구원론
  position: "개혁주의"
  emphasis: "은혜의 무조건성"
  key_texts: ["로마서 8:29-30", "에베소서 2:8-9"]
  notes: ""
eschatology:           # 종말론
  position: ""
  emphasis: ""
ecclesiology:          # 교회론
  position: ""
pneumatology:          # 성령론
  position: ""
scripture_view:        # 성경관
  position: ""
```

```yaml
# style.yaml 예시
tone: "경어체"
sentence_length: "중간 (15-25자)"
rhetoric:
  metaphor_frequency: "높음"
  favorite_metaphors: ["빛과 어둠", "씨앗과 열매"]
argumentation: "연역적"
paragraph_style: "짧은 단락 선호"
```

```yaml
# sermon_pattern.yaml 예시
structure: "귀납적"
intro_ratio: 0.15
body_ratio: 0.65
application_ratio: 0.20
illustration_frequency: "본론당 1-2회"
scripture_citation_style: "본문 직접 인용 후 해설"
```

```markdown
# vocabulary.md
## 자주 쓰는 표현
- "은혜 가운데"
- "말씀이 선포될 때"

## 피하는 표현
- (분석 결과 추가)

## 성경 인용 방식
- 개역개정 사용
- 본문 인용 시 "" 로 감싸고 장절 표기
```

- [ ] **Step 2: 검증**

### Task 4: shared/references/platform-tools.md

**Files:**
- Create: `skills/shared/references/platform-tools.md`

- [ ] **Step 1: 플랫폼 도구 매핑 문서 작성**

스펙 섹션 7의 도구 매핑 테이블 + Agent 비호환 대응 + 각 스킬에서의 사용 패턴.

포함할 내용:
- Claude Code 도구명 (확정)
- Codex / Gemini CLI 도구명 (TBD, 구현 시 검증)
- Agent 도구 비호환 대응: 순차 처리 패턴
- 스킬 내 도구 호출 시 플랫폼 중립적 표현 가이드 (예: "파일을 읽는다" → 도구명 직접 기술 대신 행위 기술)

- [ ] **Step 2: 검증**

### Task 5: shared/references/absorb-rules.md

**Files:**
- Create: `skills/shared/references/absorb-rules.md`

- [ ] **Step 1: 흡수 규칙 문서 작성**

스펙 4.3의 매칭 로직을 상세화:

포함할 내용:
- 매칭 4단계 (제목/주제, 위키링크 중첩, 카테고리 일치, LLM 판단)
- Anti-cramming 규칙 (200줄 + 독립 가능 시 분리)
- Anti-thinning 규칙 (15줄 미만 → 병합)
- 카테고리 결정 기준 (people/concepts/sermons/books/passages/references)
- 배치 처리 규칙 (15건씩, 체크포인트, 중단 재개)
- 스냅샷 자동 생성 시점
- _index.md 재구축 규칙

- [ ] **Step 2: 검증**

### Task 6: shared/references/search-strategy.md

**Files:**
- Create: `skills/shared/references/search-strategy.md`

- [ ] **Step 1: 검색 전략 문서 작성**

스펙 섹션 6의 계층적 요약 검색을 실행 가능한 수준으로 상세화:

```
Level 0: 카테고리 _index.md (또는 루트 _index.md)
  → 토큰: 최소 (제목 + 한줄 요약만)
  → 용도: 관련 기사 후보 선정

Level 1: 후보 기사의 index.md summary 필드
  → 토큰: 소 (요약만)
  → 용도: 관련성 확인 + 추가 탐색 결정

Level 2: 확정된 기사의 chunks/
  → 토큰: 필요한 만큼
  → 용도: 상세 내용 확인
```

- 검색 시작점 결정 기준 (질문 유형 → 카테고리 매핑)
- 토큰 예산 관리 가이드
- "찾지 못한 경우" 처리 (카테고리 확장, 루트 인덱스 폴백)

- [ ] **Step 2: 검증**

### Task 7: publish-setup SKILL.md

**Files:**
- Create: `skills/publish-setup/SKILL.md`

- [ ] **Step 1: SKILL.md 작성**

```markdown
---
name: publish-setup
description: Use when users say "/publish-setup", "워크스페이스 만들어줘", "publish agent 설정", or when this is the first use of publish agent skills
---

# Publish Setup — 워크스페이스 초기화

새로운 publish agent 워크스페이스를 생성하고 저자 프로필 디렉토리를 초기화한다.

## 트리거 조건

- "/publish-setup"
- "워크스페이스 만들어줘"
- "publish agent 설정"
- "출판 에이전트 시작"
- publish agent 스킬 최초 사용 감지 시

## 사전 조건

없음 (이 스킬이 모든 것의 시작점)

## WHEN TRIGGERED - EXECUTE IMMEDIATELY

### Step 1: 사용자 정보 수집

사용자에게 질문:
1. 워크스페이스 경로 (기본값 제안: ~/publish_workspace/)
2. 저자 이름
3. 교단 (선택사항)
4. 직분 (선택사항)

### Step 2: 의존성 확인

pandoc 설치 여부 확인:
- 셸에서 `pandoc --version` 실행
- 미설치 시 안내: "pandoc이 설치되어 있지 않습니다. /publish-export 기능 사용 시 필요합니다. 설치: brew install pandoc (macOS) 또는 apt install pandoc (Linux)"
- pandoc 미설치여도 진행 가능 (export만 불가)

### Step 3: 디렉토리 구조 생성

워크스페이스 구조 참조: Read `shared/references/workspace-schema.md`

생성할 디렉토리:
{workspace}/
├── authors/{author_id}/
├── wiki/people/
├── wiki/concepts/
├── wiki/sermons/
├── wiki/books/
├── wiki/passages/
├── wiki/references/
├── raw/entries/
├── projects/
├── snapshots/
└── logs/

### Step 4: 초기 파일 생성

1. config.yaml — workspace-schema.md의 스키마에 따라 사용자 입력으로 채움
2. authors/{author_id}/ — 빈 theology.yaml, style.yaml, sermon_pattern.yaml, vocabulary.md (author-profile-schema.md 참조)
3. wiki/_index.md — "# Wiki Index\n\n(아직 기사가 없습니다)"
4. wiki/{category}/_index.md — 각 카테고리별 빈 인덱스
5. wiki/_backlinks.json — {}
6. wiki/_absorb_log.json — {"batches": [], "pending_entries": []}

### Step 5: 완료 리포트

사용자에게 보고:
- 워크스페이스 경로
- 생성된 디렉토리/파일 수
- 다음 단계 안내: "자료를 수집할 준비가 되었습니다. 기존 설교문, 저서, 글 등이 있는 폴더 경로나 URL을 알려주세요."

## 참조 문서
- shared/references/workspace-schema.md
- shared/references/author-profile-schema.md
```

- [ ] **Step 2: 검증**

스킬 파일을 읽어서 확인:
- frontmatter (name, description) 존재
- 트리거 조건 한/영 포함
- "WHEN TRIGGERED - EXECUTE IMMEDIATELY" 패턴
- 참조 문서 경로 정확
- 스펙의 5.0 워크플로우와 일치

- [ ] **Step 3: 커밋**

```bash
git add skills/shared/ skills/publish-setup/
git commit -m "feat: add shared references and publish-setup skill"
```

---

## Chunk 2: publish-collect + publish-absorb

온보딩 파이프라인의 핵심. 자료 수집과 KB 흡수.

### Task 8: publish-collect/references/format-handling.md

**Files:**
- Create: `skills/publish-collect/references/format-handling.md`

- [ ] **Step 1: 파일 형식 처리 규칙 문서 작성**

포함할 내용:
- 지원 형식별 처리 방법:
  - .md → 그대로 사용, 프론트매터만 추가
  - .txt → 마크다운으로 감싸기, 인코딩 감지
  - .docx → pandoc으로 변환 (`pandoc -f docx -t markdown`)
  - .pdf → 텍스트 추출 (`pdftotext` 또는 pandoc), 이미지 PDF 감지 시 사용자 안내
  - 웹 URL → WebFetch로 가져와서 마크다운 정제
- 인코딩 감지: `file --mime-encoding` → EUC-KR/CP949이면 `iconv`로 UTF-8 변환
- content_hash 계산: 정제된 마크다운 본문의 SHA-256
- 에러 처리 테이블 (스펙 섹션 8)
- raw entry 프론트매터 템플릿 (스펙 4.2)

- [ ] **Step 2: 검증**

### Task 9: publish-collect SKILL.md

**Files:**
- Create: `skills/publish-collect/SKILL.md`

- [ ] **Step 1: SKILL.md 작성**

핵심 구조:

```markdown
---
name: publish-collect
description: Use when users say "/publish-collect", "자료 수집해줘", "이 파일들 분석해줘", "이 URL에서 가져와", or want to add source materials to the knowledge base
---

# Publish Collect — 자료 수집

로컬 파일 및 웹 URL에서 자료를 수집하여 raw/entries/에 정제된 마크다운으로 저장한다.

## 트리거 조건
{한/영 트리거 목록}

## 사전 조건
- publish-setup 완료 (config.yaml 존재)

## WHEN TRIGGERED - EXECUTE IMMEDIATELY

### Step 1: config.yaml 로드
- 워크스페이스 경로 확인
- defaults.source_type, defaults.encoding 로드

### Step 2: 입력 분석
- 사용자가 제공한 경로/URL 파악
- 디렉토리면 내부 파일 목록화
- 자료 유형 확인 (primary/reference) — 미지정 시 defaults.source_type 사용

### Step 3: 파일별 처리
- format-handling.md 참조
- 각 파일: 형식 감지 → 인코딩 정규화 → 마크다운 변환
- content_hash 계산 → raw/entries/ 기존 항목과 중복 체크
- 중복 시 건너뛰기 + 로그

### Step 4: raw entry 저장
- 파일명: {YYYYMMDD}_{source_id}.md
- 프론트매터: workspace-schema.md의 raw entry 스키마
- batch_id: batch_{YYYYMMDD} (이번 수집 세션)

### Step 5: 수집 리포트
- 총 N건 수집, M건 중복 건너뜀
- 형식별 분류 (md: X, docx: Y, pdf: Z, url: W)
- 유형별 분류 (primary: A, reference: B)
- 다음 단계 안내: "수집이 완료되었습니다. 위키에 흡수할까요?"

## 참조 문서
- shared/references/workspace-schema.md
- publish-collect/references/format-handling.md
```

- [ ] **Step 2: 검증**

### Task 10: publish-absorb/references/absorb-prompt.md

**Files:**
- Create: `skills/publish-absorb/references/absorb-prompt.md`

- [ ] **Step 1: 흡수용 프롬프트 템플릿 작성**

absorb 시 LLM이 각 항목을 분석할 때 사용하는 내부 프롬프트 템플릿:

```markdown
# 흡수 분석 프롬프트

## 항목 분석
이 항목을 읽고 다음을 판단하라:
1. 핵심 주제는 무엇인가? (제목이 아닌 의미)
2. 어떤 카테고리에 속하는가? (people/concepts/sermons/books/passages/references)
3. 기존 기사 중 매칭되는 것이 있는가? (후보 목록 제공)
4. 매칭되면: 기존 기사에 병합할 내용은? 분리할 하위 주제는?
5. 매칭 안 되면: 새 기사의 제목, 요약, 관련 위키링크는?

## 기사 작성 규칙
- 톤: 백과사전식, 중립적 (LLM Wiki 방식)
- 저자의 1차 자료: "저자는 ~라고 주장한다", "저자의 입장은 ~이다"
- 참고 자료: "~에 따르면", "~는 ~라고 설명한다"
- 위키링크: 관련 개념마다 [[]] 적용
- 요약: 기사 상단에 2-3문장 요약 필수
- 최소 15줄, 최대 200줄 (초과 시 분리 검토)

## 청크 분리 기준
- 기사 본문이 100줄 이상이면 주제별로 chunks/ 분리
- 각 chunk는 자체적으로 읽을 수 있는 완결된 섹션
- chunk 파일명: 001.md, 002.md (순서대로)
```

- [ ] **Step 2: 검증**

### Task 11: publish-absorb SKILL.md

**Files:**
- Create: `skills/publish-absorb/SKILL.md`

- [ ] **Step 1: SKILL.md 작성**

핵심 구조:

```markdown
---
name: publish-absorb
description: Use when users say "/publish-absorb", "위키 업데이트해줘", "자료 정리해줘", or after collect is complete and wiki needs to be updated
---

# Publish Absorb — 위키 흡수

raw/entries/의 미흡수 항목을 분석하여 wiki/ 기사로 컴파일한다. LLM Wiki의 absorption 패턴.

## 트리거 조건
{한/영 트리거}

## 사전 조건
- config.yaml 존재
- raw/entries/에 absorbed: false 항목 존재

## WHEN TRIGGERED - EXECUTE IMMEDIATELY

### Step 0: 스냅샷 생성
- snapshots/{timestamp}/ 디렉토리 생성
- wiki/_index.md, wiki/_backlinks.json 사본 저장
- manifest.json 생성 (trigger: "pre_absorb")

### Step 1: 미흡수 항목 스캔
- raw/entries/ 전체 스캔
- 각 파일의 프론트매터에서 absorbed: false && deleted: false 필터
- _absorb_log.json의 pending_entries 확인 (중단 재개)
- batch_size (config.yaml defaults.batch_size, 기본 15) 단위로 그룹핑

### Step 2: 배치 처리
각 배치(15건)에 대해:

#### 2a: 항목 분석
각 항목마다:
- 원본 읽기
- absorb-prompt.md의 프롬프트로 분석
- absorb-rules.md의 매칭 로직으로 기존 기사 후보 선정

#### 2b: 기사 생성/갱신
- wiki-article-format.md 참조
- 매칭됨: 기존 기사 재읽기 → 내용 병합 → updated 날짜 갱신
- 매칭 안 됨: 새 기사 디렉토리 생성 → index.md + chunks/ 작성
- 개념 기사(concepts/) 패턴 감지 시 자동 생성/갱신

#### 2c: 링크 업데이트
- 위키링크 추출 → _backlinks.json 갱신
- 관련 기사의 related 필드 상호 업데이트

#### 2d: 체크포인트
- 각 항목 absorbed: true 마킹
- _absorb_log.json 갱신 (entries_processed 카운트)

### Step 3: 인덱스 재구축
- wiki/_index.md 전체 재생성 (모든 기사 제목 + summary 한줄)
- 각 카테고리 _index.md 재생성
- _backlinks.json 최종 정리

### Step 4: 흡수 리포트
- N건 처리, 기사 M개 생성, K개 갱신
- 새로 발견된 개념 기사 목록
- 다음 단계 안내

## 참조 문서
- shared/references/workspace-schema.md
- shared/references/wiki-article-format.md
- shared/references/absorb-rules.md
- publish-absorb/references/absorb-prompt.md
```

- [ ] **Step 2: 검증**

- [ ] **Step 3: 커밋**

```bash
git add skills/publish-collect/ skills/publish-absorb/
git commit -m "feat: add publish-collect and publish-absorb skills"
```

---

## Chunk 3: publish-profile + publish-write + publish-review

저자 분석, 집필, 심사 — 핵심 저작 파이프라인.

### Task 12: publish-profile/references/analysis-dimensions.md

**Files:**
- Create: `skills/publish-profile/references/analysis-dimensions.md`

- [ ] **Step 1: 분석 차원 문서 작성**

4개 분석 차원별 구체적 기준:

1. **문체 (style.yaml)**
   - 어투 (경어/반말/혼합)
   - 문장 평균 길이 (단어 수)
   - 수사법 목록 (은유, 직유, 대조, 반복, 열거 등)
   - 비유 패턴 (자주 쓰는 비유 소재)
   - 논증 방식 (연역/귀납/예화 중심)
   - 단락 길이 경향

2. **신학적 입장 (theology.yaml)**
   - 분석 항목: 구원론, 종말론, 교회론, 성령론, 성경관, 예정론, 성례론
   - 각 항목별: 입장(position), 강조점(emphasis), 근거 본문(key_texts)
   - 주의: 저자의 실제 입장을 기록, 평가하지 않음

3. **설교 구조 (sermon_pattern.yaml)**
   - 구조 유형 (귀납/연역/내러티브/대화/주제)
   - 서론-본론-적용 비율
   - 예화 빈도와 유형
   - 성경 인용 방식 (직접 인용/의역/비율)
   - 청중 호칭 방식

4. **어휘 패턴 (vocabulary.md)**
   - 자주 쓰는 표현 (빈도 기반)
   - 피하는 표현/단어
   - 성경 번역본 (개역개정/새번역/NIV 등)
   - 인용 표기 형식
   - 특징적인 전환어/접속어

- [ ] **Step 2: 검증**

### Task 13: publish-profile SKILL.md

**Files:**
- Create: `skills/publish-profile/SKILL.md`

- [ ] **Step 1: SKILL.md 작성**

```markdown
---
name: publish-profile
description: Use when users say "/publish-profile", "내 문체 분석해줘", "프로필 업데이트", or after a large batch of new materials has been absorbed
---
```

핵심 워크플로우:
1. config.yaml에서 author_id 확인
2. 분석 소스 결정: wiki/ 기사 + raw/entries/ 원본 샘플링
3. 4개 차원 분석 (analysis-dimensions.md 참조)
4. 기존 프로필 존재 시: diff 생성 → 변경점 사용자에게 제시 → 승인 후 갱신
5. 신규 프로필: 전체 생성 → 사용자 검토 → 확정

주의사항:
- primary 자료만 분석 대상 (reference 제외)
- 최소 5건 이상의 자료가 있어야 신뢰도 있는 분석 가능
- 분석 결과에 대해 사용자 확인 필수 (자동 덮어쓰기 금지)

- [ ] **Step 2: 검증**

### Task 14: publish-write/references/writing-modes.md

**Files:**
- Create: `skills/publish-write/references/writing-modes.md`

- [ ] **Step 1: 집필 모드 가이드 작성**

4가지 프로젝트 유형별 가이드:

1. **new_book (신규 도서)**
   - 사용자로부터 목차 수집 또는 KB 기반 자동 제안
   - 챕터별 순차 작성
   - 각 챕터: wiki/ 검색 → 관련 자료 로드 → 프로필 기반 작성
   - 자기 검증 체크리스트

2. **revision (개정판)**
   - 원본 문서 로드 (project.yaml의 base_document)
   - KB 최신 상태와 비교 → 변경/추가 필요 부분 식별
   - 섹션별 업데이트 제안 → 사용자 승인 → 수정

3. **sermon_collection (설교집)**
   - wiki/sermons/ 기사 기반 구성
   - 시간순/주제순 정렬 옵션
   - 서문, 소개글 자동 생성
   - 설교 간 연결 해설 추가

4. **commentary (강해서)**
   - 성경 본문 단위 구성 (wiki/passages/ 기반)
   - 본문-해설-적용 구조
   - 원어 참고자료 통합 (wiki/references/)

공통:
- wiki/ 검색 전략: search-strategy.md 참조
- 프로필 로드: style.yaml + theology.yaml + sermon_pattern.yaml + vocabulary.md
- 토큰 관리: 챕터 단위 작업, 이전 챕터 요약만 유지

- [ ] **Step 2: 검증**

### Task 15: publish-write SKILL.md

**Files:**
- Create: `skills/publish-write/SKILL.md`

- [ ] **Step 1: SKILL.md 작성**

```markdown
---
name: publish-write
description: Use when users say "/publish-write", "책 써줘", "초안 작성", "개정판 수정해줘", "설교집 정리해줘", or want to draft or revise a book/sermon collection
---
```

핵심 워크플로우:
1. 프로젝트 유형 + 주제/목차 확인
2. projects/{name}/ 생성, project.yaml 초기화
3. 저자 프로필 전체 로드
4. 챕터별: search-strategy.md로 wiki/ 검색 → 관련 자료 수집 → 초안 작성
5. 자기 검증 (프로필 대비 문체/관점 체크)
6. drafts/ 저장 + 리포트

- [ ] **Step 2: 검증**

### Task 16: publish-review/references/review-rubric.md

**Files:**
- Create: `skills/publish-review/references/review-rubric.md`

- [ ] **Step 1: 심사 기준표 작성**

4차원 심사 루브릭:

```markdown
# 심사 기준표

## 1. 문체 일관성 (Style Consistency)
기준: style.yaml + vocabulary.md

| 등급 | 기준 |
|------|------|
| A (우수) | 어투, 문장 길이, 수사법이 프로필과 95% 이상 일치 |
| B (양호) | 대부분 일치하나 일부 문장에서 어색한 표현 |
| C (보통) | 전반적 톤은 맞지만 세부 패턴 불일치 다수 |
| D (미흡) | 프로필과 명확히 다른 문체 |

## 2. 신학적 일관성 (Theological Consistency)
기준: theology.yaml — 저자의 관점 기준, 절대적 정답 아님

| 등급 | 기준 |
|------|------|
| A | 저자의 신학적 입장과 완전히 일관 |
| B | 대체로 일관하나 모호한 표현 1-2곳 |
| C | 저자의 입장과 미묘하게 다른 뉘앙스 있음 |
| D | 저자의 입장과 상충하는 내용 포함 |

## 3. 논리 구조 / 설득력
{등급별 기준}

## 4. 문법 / 맞춤법 / 가독성
{등급별 기준}

## 종합 판정
- 전 차원 B 이상: PASS
- C 1개 이하: CONDITIONAL (해당 부분만 수정)
- D 포함 또는 C 2개 이상: REVISE (재작성 권고)
```

- [ ] **Step 2: 검증**

### Task 17: publish-review SKILL.md

**Files:**
- Create: `skills/publish-review/SKILL.md`

- [ ] **Step 1: SKILL.md 작성**

```markdown
---
name: publish-review
description: Use when users say "/publish-review", "검토해줘", "교정해줘", "심사해줘", or after a draft is completed and needs review
---
```

핵심 워크플로우:
1. 심사 대상 파일 확인 (drafts/ 내)
2. 저자 프로필 전체 로드
3. wiki/ 관련 기사 로드 (KB 기반 심사)
4. review-rubric.md 기준 4차원 심사
5. 심사 리포트 생성 → reviews/{date}_review.md
6. 사용자 확인 → 승인된 수정사항 반영
7. 재심사 루프 (최대 config.yaml review_max_rounds회)
8. 3회 후 미해결 시 사용자 판단 위임

soft delete 정의 포함 (스펙 5.5)

- [ ] **Step 2: 검증**

- [ ] **Step 3: 커밋**

```bash
git add skills/publish-profile/ skills/publish-write/ skills/publish-review/
git commit -m "feat: add publish-profile, publish-write, and publish-review skills"
```

---

## Chunk 4: publish-curate + publish-export + publish-sermon

지원 스킬들.

### Task 18: publish-curate SKILL.md

**Files:**
- Create: `skills/publish-curate/SKILL.md`

- [ ] **Step 1: SKILL.md 작성**

```markdown
---
name: publish-curate
description: Use when users say "/publish-curate", "위키 정리해줘", "잘못된 자료 확인", "배치 롤백", or want to clean up or fix the knowledge base
---
```

핵심 워크플로우:
1. 검수 범위 확인 (전체 / 특정 batch_id / 특정 source_id)
2. 저자 프로필 로드
3. 대상 기사/항목 스캔 → 프로필 기준 이질성 감지
4. 플래그 리포트 (기사명, 이질성 유형, 출처, 심각도)
5. 사용자 선택: 개별 soft delete / 배치 롤백 / 무시
6. 실행:
   - soft delete: 프론트매터 deleted: true
   - 배치 롤백: snapshots/에서 해당 시점 복원
7. _index.md, _backlinks.json 재구축

참조: workspace-schema.md (스냅샷), absorb-rules.md

- [ ] **Step 2: 검증**

### Task 19: publish-export SKILL.md

**Files:**
- Create: `skills/publish-export/SKILL.md`

- [ ] **Step 1: SKILL.md 작성**

```markdown
---
name: publish-export
description: Use when users say "/publish-export", "PDF로 만들어줘", "출판용 파일", "ePub 변환", or want to convert drafts to publishable formats
---
```

핵심 워크플로우:
1. pandoc 설치 확인 (미설치 시 설치 안내 후 중단)
2. 대상 프로젝트 + 출력 포맷 확인 (DOCX/PDF/ePub)
3. project.yaml의 outline 순서대로 drafts/ 취합
4. 목차, 표지 정보 구성
5. pandoc 변환:
   - DOCX: `pandoc -f markdown -t docx --toc`
   - PDF: `pandoc -f markdown -t pdf --pdf-engine=xelatex --variable mainfont="Noto Sans KR"` (한글 폰트)
   - ePub: `pandoc -f markdown -t epub --toc`
6. exports/{format}/ 저장
7. 완료 리포트 (파일 경로)

주의: 한글 PDF는 xelatex + 한글 폰트 필요. 미설치 시 안내.

- [ ] **Step 2: 검증**

### Task 20: publish-sermon SKILL.md

**Files:**
- Create: `skills/publish-sermon/SKILL.md`

- [ ] **Step 1: SKILL.md 작성**

```markdown
---
name: publish-sermon
description: Use when users say "/publish-sermon", "설교 준비 도와줘", "에 대해 내가 뭐라고 했지", "자료 찾아줘", or want sermon preparation assistance from the knowledge base
---
```

핵심 워크플로우:
1. 사용자 질문/요청 파악 (자연어 또는 성경 본문)
2. config.yaml 로드 → 워크스페이스 경로
3. search-strategy.md 기반 wiki/ 계층 검색:
   - 성경 본문 질문 → passages/ 우선 → concepts/ → sermons/
   - 주제 질문 → concepts/ 우선 → sermons/ → references/
   - "내가 뭐라고 했지" → sermons/ 우선 → books/ → concepts/
4. 관련 기사 종합:
   - 저자 과거 설교 요약
   - 저자의 해당 주제 입장
   - 관련 성경 본문 기사
   - 참고자료 (reference 타입)
5. 설교 준비 자료 제시:
   - 관련 본문과 해석
   - 과거 설교에서 다룬 방식
   - 참고할 수 있는 외부 자료
   - 저자의 신학적 입장 요약

- [ ] **Step 2: 검증**

- [ ] **Step 3: 커밋**

```bash
git add skills/publish-curate/ skills/publish-export/ skills/publish-sermon/
git commit -m "feat: add publish-curate, publish-export, and publish-sermon skills"
```

---

## Chunk 5: 스킬 설치 설정 + 통합 검증

### Task 21: 프로젝트 루트 파일

**Files:**
- Create: `CLAUDE.md` (프로젝트 가이드)
- Create: `skills/README.md` (스킬 목록 + 설치 가이드)

- [ ] **Step 1: CLAUDE.md 작성**

```markdown
# Publish Agent

저자의 기존 저서·설교·글을 분석하여 개인 신학 위키(KB)를 구축하고,
저자의 문체·신학관·설교구조를 습득한 상태에서
새 책 집필, 기존 책 개정, 설교 준비를 지원하는 LLM 스킬 시스템.

## 스킬 목록
{9개 스킬 + 한줄 설명}

## 설치
{~/.claude/skills/에 심볼릭 링크 또는 복사 안내}

## 사용법
{온보딩 → 일상 사용 흐름}

## 설계 문서
- docs/specs/2026-04-21-publish-agent-design.md
```

- [ ] **Step 2: skills/README.md 작성**

스킬 목록, 의존 관계 다이어그램, 각 스킬 설치 방법.

- [ ] **Step 3: 검증**

모든 스킬 파일이 존재하는지 확인:
```bash
ls -la skills/*/SKILL.md
ls -la skills/shared/references/*.md
ls -la skills/publish-*/references/*.md
```

- [ ] **Step 4: 최종 커밋**

```bash
git add CLAUDE.md skills/README.md
git commit -m "feat: add project guide and skills README"
```

---

## Task Dependencies

```
Task 1-6 (shared refs) → Task 7 (setup)
                       → Task 8-9 (collect)
                       → Task 10-11 (absorb)
Task 1-6             → Task 12-13 (profile)
                       → Task 14-15 (write)
                       → Task 16-17 (review)
                       → Task 18 (curate)
                       → Task 19 (export)
                       → Task 20 (sermon)
Task 1-20              → Task 21 (root files + validation)
```

공유 리소스(Task 1-6)가 먼저 완료되면, Task 7-20은 병렬 실행 가능.

## Execution Notes

- 이 프로젝트는 코드가 아닌 **스킬 파일(마크다운)** 작성이므로, TDD 대신 "스펙 대비 검증" 패턴을 사용한다.
- 각 스킬 작성 후 검증: frontmatter 존재, 트리거 조건 포함, 워크플로우가 스펙과 일치, 참조 문서 경로 정확.
- 스킬 간 참조 경로는 상대 경로 (`shared/references/...`) 사용. 설치 시 심볼릭 링크로 해결.
