# 설교 팩 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development. Steps use checkbox syntax.

**Goal:** 설교 코퍼스 실측 fingerprint → 수치 팩 → stdlib 기계 게이트 → 스킬 연동.

**Architecture:** 스펙 `docs/specs/2026-07-18-sermon-pack-design.md`가 정본. Python 스크립트 2개(stdlib) + 스키마 reference 1개 + SKILL.md 3종 최소 수정.

## Global Constraints
- Python 3.9+ stdlib only (Windows 호환: UTF-8 명시, 경로 하드코딩 금지).
- 이 리포는 스킬 리포 — venv 없음. 테스트: `python3 -m pytest tests/ -q` (pytest 없으면 `pip3 install --user pytest`).
- church 브랜치 merge 안전: 기존 SKILL.md 수정은 섹션 추가 위주 최소 diff.
- 커밋 끝: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`

---

### Task 1: scripts/sermon_fingerprint.py (TDD)

**Files:** Create `scripts/sermon_fingerprint.py`, `tests/test_fingerprint.py`, `tests/fixtures/corpus/` (합성 설교 3편)

**Interfaces:**
- CLI: `python3 scripts/sermon_fingerprint.py <corpus_dir> [-o out.json]` — .md/.txt 재귀 수집, JSON 출력.
- 모듈: `fingerprint(texts: list[str]) -> dict` — 스펙 ①의 측정 항목 전부. 키:
  `n_docs, n_sents, sent_words: {p10,p50,p90,mean}, endings: {패턴: 비율}, punct_per_1k: {period,comma,question,exclam,ellipsis,quote}, markers_per_1k_words: {ordinal,adversative,vocative}, self_ref_per_1k_words, bible_refs_per_1k_chars, para: {sents_p50, blank_ratio}`
- 문장 분리: `(?<=[.!?…])\s+` 기반 + 장절 괄호 `(요 3:16)` 보호(분리 전 마스킹).
- 어미 패턴(정규식, 문장 끝 어절 대상): 습니다/ㅂ니다(합니다·됩니다…)/아요·어요/죠/니까(까)/다(평서)/ㅂ시다/십시오/으라·라/기타 `_other`.
- 백분위: `statistics.quantiles` 또는 정렬 인덱스(n<20 안전).

**Steps:** 합성 코퍼스 픽스처(경어체 설교 2편 + 반말 1편, 성경 인용·첫째둘째·"사랑하는 성도 여러분" 포함, 각 15문장+) 작성 → 실패 테스트(p50 어절 수 기대범위, endings에 습니다 최상위, vocative>0, bible_refs>0, 빈 폴더 에러) → FAIL → 구현 → PASS → Commit `feat: sermon corpus fingerprint script`

---

### Task 2: scripts/verify_sermon.py (TDD)

**Files:** Create `scripts/verify_sermon.py`, `tests/test_verify.py`, `tests/fixtures/rules.json`

**Interfaces:**
- CLI: `python3 scripts/verify_sermon.py <draft.md> --fingerprint fp.json --rules rules.json [--json]` — stdout에 결과 JSON `{"ok": bool, "violations": [{check, expected, actual, evidence}]}`, exit ok?0:1.
- 모듈: `verify(draft_text: str, fp: dict, rules: dict) -> dict`.
- 검사 4종(스펙 ③): bands(초안을 fingerprint()로 실측해 대조 — Task 1 모듈 import), must_zero(부분 문자열 매치, 발견 문장을 evidence로), ai_tells(내장 DEFAULT_AI_TELLS + rules 추가분), signatures(min_per_doc 미달).
- rules.json에 없는 검사는 스킵(부분 rules 허용).

**Steps:** 실패 테스트(밴드 위반 초안 ok:false+evidence, must_zero 검출, 시그니처 미달, 전부 준수 ok:true, 부분 rules 스킵) → FAIL → 구현 → PASS → Commit `feat: sermon draft verification gate`

---

### Task 3: 팩 스키마 + SKILL.md 연동 + E2E

**Files:** Create `skills/shared/references/sermon-pack-schema.md`; Modify `skills/publish-profile/SKILL.md`, `skills/publish-write/SKILL.md`, `skills/publish-sermon/SKILL.md`, `skills/publish-review/SKILL.md`; Create `tests/test_e2e.py`

**Work:**
- sermon-pack-schema.md: 스펙 ②의 6섹션 스키마 + rules.json 스키마 + "수치는 fingerprint 실측만 인용" 규칙 + custom-sermon-pack.md 우선 규칙.
- SKILL.md 수정(각각 "## 설교 팩" 섹션 추가, 기존 본문 최소 변경):
  - profile: fingerprint 실행 → sermon-pack.md + rules.json 생성 절차
  - write/sermon: 팩 로드 제약 + 초안 후 verify 실행·재작성(최대 2회) 절차
  - review: 게이트 선행 확인 + 리포트에 실측치 표
- E2E 테스트: 픽스처 코퍼스 → fingerprint → 간단 rules 생성 → 위반 초안(반말+AI상투구) ok:false / 준수 초안 ok:true.

**Steps:** 스키마·SKILL 수정 → E2E 테스트 작성·통과 → 전체 `python3 -m pytest tests/ -q` → Commit `feat: sermon pack schema + skill integration`
