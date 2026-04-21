# Publish Agent

저자의 기존 저서·설교·글을 분석하여 개인 신학 위키(KB)를 구축하고,
저자의 문체·신학관·설교구조를 습득한 상태에서
새 책 집필, 기존 책 개정, 설교 준비를 지원하는 LLM 스킬 시스템.

## 스킬 목록

| 스킬 | 역할 |
|------|------|
| `/publish-setup` | 워크스페이스 초기화, 저자 기본 정보 |
| `/publish-collect` | 로컬/웹 자료 수집 (1차·2차 자료) |
| `/publish-absorb` | raw entries → 위키 기사 흡수 (LLM Wiki 패턴) |
| `/publish-profile` | 저자 프로필 분석/갱신 (문체·신학·설교구조·어휘) |
| `/publish-write` | KB + 프로필 기반 집필 (신규/개정/설교집/강해서) |
| `/publish-review` | KB + 프로필 기반 교정/심사 (4차원 루브릭) |
| `/publish-curate` | KB 검수/오염 제거/롤백 |
| `/publish-export` | Markdown → DOCX/PDF/ePub 변환 |
| `/publish-sermon` | 설교 준비용 KB 조회 |

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

이렇게 하면 모든 스킬이 `~/.claude/skills/publish-agent/` 하위에 위치하며,
스킬 내부의 `shared/references/...` 등 상대 경로가 `skills/` 루트 기준으로 자연스럽게 해석됩니다.

## 설치 확인 (Windows)

```powershell
pandoc --version
py -3 --version
pdftotext -v        # PDF 수집용 (선택)
xelatex --version   # PDF export용 (선택)
```

## 사용법

스킬 설치 후 Claude Code에서 `/publish-agent/publish-setup` 형식으로 호출하거나,
자연어로 대화하면 적절한 스킬이 자동 호출됩니다.

### 온보딩 (첫 1회)
1. "워크스페이스 만들어줘" → setup
2. "내 설교 파일들 수집해줘" → collect
3. (자동) → absorb → 위키 구축
4. (자동) → profile → 저자 프로필 생성

### 일상 사용
자연어로 대화하면 LLM이 적절한 스킬을 자동 호출합니다.
- "새 책 써줘" → write → review → export
- "설교 준비 도와줘" → sermon
- "새 자료 추가해줘" → collect → absorb

## 플랫폼
현재 Claude Code 기준으로 검증됨. Codex (OpenAI), Gemini CLI 이식은 도구 매핑(platform-tools.md) 기반으로 가능하나 아직 검증되지 않음.

## 설계 문서
- `docs/specs/2026-04-21-publish-agent-design.md`
- `docs/plans/2026-04-22-publish-agent-skills.md`
