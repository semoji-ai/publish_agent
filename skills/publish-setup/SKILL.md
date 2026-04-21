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

## WHEN TRIGGERED - EXECUTE IMMEDIATELY

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

셸에서 pandoc 설치 여부를 확인한다:

```bash
pandoc --version
```

- **설치됨:** pandoc 버전 기록, 진행
- **미설치:** 안내 메시지 출력 후 진행 (export만 불가)
  ```
  pandoc이 설치되어 있지 않습니다.
  /publish-export 기능 사용 시 필요합니다.
  설치 방법:
    macOS:   brew install pandoc
    Linux:   sudo apt install pandoc
    Windows: choco install pandoc
             또는 winget install pandoc
  지금은 건너뛰고 나중에 설치해도 됩니다.
  ```

### Step 3: 디렉토리 구조 생성

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
  encoding: utf-8

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
pandoc: {설치됨 v{버전} / 미설치}

다음 단계:
기존 설교문, 저서, 글 등이 있는 폴더 경로나 URL을 알려주세요.
자료를 수집하여 나만의 신학 위키를 구축합니다.
```

---

## 참조 문서

- `shared/references/workspace-schema.md` — 워크스페이스 구조 + 전체 스키마
- `shared/references/author-profile-schema.md` — 저자 프로필 4파일 스키마
