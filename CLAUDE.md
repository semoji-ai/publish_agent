# Publish Agent

저자의 기존 저서·설교·글을 분석하여 개인 신학 위키(KB)를 구축하고,
저자의 문체·신학관·설교구조를 습득한 상태에서
새 책 집필, 기존 책 개정, 설교 준비를 지원하는 LLM 스킬 시스템.

---

## 브랜치 전략

이 프로젝트는 **코어 + 사용자별 브랜치** 구조로 운영된다.

```
main                    ← 코어 (공통 기능, 버그 수정, 새 기능)
├── church/piel         ← 피엘교회 특화
├── church/sarang       ← 사랑교회 특화
└── church/{name}       ← 새 사용자 추가 시
```

### 규칙

1. **공통 수정은 반드시 `main`에서 작업** → 각 `church/*` 브랜치에 merge
2. **사용자별 특화는 해당 `church/*` 브랜치에서만 작업** → main으로 merge하지 않음
3. **커스텀은 기존 파일 수정 대신 별도 파일 추가** → merge 충돌 최소화
   - `review-rubric.md` 수정 ❌
   - `custom-rubric.md` 추가 ✅
4. **SKILL.md에서 `custom-*.md` 파일이 있으면 우선 적용**하도록 작성

### 새 사용자 온보딩

```bash
git checkout main
git checkout -b church/{name}
# custom-*.md 파일 추가, export 템플릿 등 커스텀
git push origin church/{name}
```

### 코어 업데이트 시 각 브랜치 반영

```bash
git checkout main
# 수정 + 커밋 + 푸시

# 각 사용자 브랜치에 반영
git checkout church/piel
git merge main
# 충돌 해결 (custom-*.md는 충돌 안 남)
git push
```

---

## 커스텀 파일 규칙

사용자별 특화 파일은 `custom-` 접두사를 사용한다.

```
skills/
├── publish-write/
│   └── references/
│       ├── writing-modes.md       ← 공통 (main)
│       └── custom-modes.md        ← 사용자별 추가 모드 (branch)
├── publish-review/
│   └── references/
│       ├── review-rubric.md       ← 공통 (main)
│       └── custom-rubric.md       ← 사용자별 심사 기준 (branch)
├── publish-export/
│   └── templates/                  ← 사용자별 export 템플릿 (branch)
│       └── church-letterhead.yaml
└── publish-sermon/
    └── references/
        └── custom-sources.md      ← 사용자별 추가 수집 소스 (branch)
```

**적용 우선순위:** `custom-*.md` 존재 시 → custom 우선, 없으면 → 공통 파일 사용

---

## 스킬 목록

| 스킬 | 역할 |
|------|------|
| `/publish-setup` | 워크스페이스 초기화, 저자 기본 정보 |
| `/publish-collect` | 로컬/웹 자료 수집 (1차·2차 자료) |
| `/publish-absorb` | raw entries → 위키 기사 흡수 (LLM Wiki 패턴) |
| `/publish-profile` | 저자 프로필 분석/갱신 (문체·신학·설교구조·어휘) |
| `/publish-plan` | 소크라테스 인터뷰 기반 기획 (컨셉·독자·메시지·구조·상세) |
| `/publish-write` | KB + 프로필 기반 집필 (신규/개정/설교집/강해서) |
| `/publish-review` | KB + 프로필 기반 교정/심사 (4차원 루브릭) |
| `/publish-curate` | KB 검수/오염 제거/롤백 |
| `/publish-export` | Markdown → DOCX/PDF/ePub 변환 |
| `/publish-sermon` | 설교 준비용 KB 조회 |

---

## 설치

`skills/` 디렉토리 전체를 `~/.claude/skills/publish-agent`로 연결:

```bash
# macOS/Linux
ln -sf "$(pwd)/skills" ~/.claude/skills/publish-agent
```

```powershell
# Windows (PowerShell)
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\publish-agent" -Target "$(Get-Location)\skills"
```

스킬 내부의 `shared/references/...` 등 상대 경로가 `skills/` 루트 기준으로 해석됩니다.

## 설치 확인 (Windows)

```powershell
pandoc --version
py -3 --version
pdftotext -v        # PDF 수집용 (선택)
xelatex --version   # PDF export용 (선택)
```

---

## 사용법

### 온보딩 (첫 1회)
1. "워크스페이스 만들어줘" → setup
2. "내 설교 파일들 수집해줘" → collect
3. (자동) → absorb → 위키 구축
4. (자동) → profile → 저자 프로필 생성

### 일상 사용
자연어로 대화하면 LLM이 적절한 스킬을 자동 호출합니다.
- "새 책 기획해줘" → plan → write → review → export
- "설교 준비 도와줘" → sermon
- "새 자료 추가해줘" → collect → absorb

---

## 개발 가이드

### 코어 수정 시 (main 브랜치)

- 모든 사용자에게 영향이 가는 변경
- SKILL.md 워크플로우 수정, shared/references/ 수정, 버그 수정
- 수정 후 **모든 활성 `church/*` 브랜치에 merge 필요**
- 기존 파일의 인터페이스(프론트매터 필드, 참조 경로)를 바꿀 때는 하위 호환성 주의

### 사용자 특화 시 (church/* 브랜치)

- 해당 사용자에게만 적용되는 변경
- `custom-*.md` 파일 추가가 기본 방식
- SKILL.md 자체를 수정해야 하면 해당 브랜치에서만 수정
- main에서 merge 받을 때 충돌 가능성 인지하고 작업

### 새 스킬 추가 시

1. main에서 `skills/{skill-name}/SKILL.md` 생성
2. frontmatter: `name`, `description` (한/영 트리거 포함)
3. `WHEN TRIGGERED - EXECUTE IMMEDIATELY` 패턴 준수
4. 참조 문서는 `skills/{skill-name}/references/`에 배치
5. 공유 참조는 `shared/references/`에 배치
6. 컨텍스트 관리: `context-management.md` 규칙 준수 (500줄 제한, 토큰 예산)

### 컨텍스트 관리 (필수)

- 500줄 이상 파일은 분할 처리
- Read 시 offset/limit 파라미터 활용
- 스킬별 토큰 예산은 `shared/references/context-management.md` 참조
- 위키 검색은 반드시 계층적 (index → summary → chunks)

---

## 플랫폼

현재 Claude Code 기준으로 검증됨. Codex (OpenAI), Gemini CLI 이식은 도구 매핑(platform-tools.md) 기반으로 가능하나 아직 검증되지 않음.

## 설계 문서
- `docs/specs/2026-04-21-publish-agent-design.md`
- `docs/plans/2026-04-22-publish-agent-skills.md`
- `docs/reviews/` — 코덱스 리뷰 및 수정 이력
