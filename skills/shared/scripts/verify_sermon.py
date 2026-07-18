#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_sermon.py — 설교 초안 기계 검증 게이트 (stdlib only, Python 3.9+)

초안을 sermon_fingerprint.fingerprint()로 실측해 팩(fingerprint.json)과
rules.json 대비 4종 검사를 수행한다: bands, must_zero, ai_tells, signatures.

band 지표 `ending_family_share`는 fingerprint의 endings 딕셔너리 중
존댓말 어미 계열(습니다 + ㅂ니다)을 합산한 값이다 — 두 버킷을 하나의
literal 종결 패턴으로 오인하지 않도록 이름을 family로 명시한다.
(family = {습니다, ㅂ니다})

CLI:
    python3 "{skill_root}/shared/scripts/verify_sermon.py" <draft.md> --fingerprint fp.json --rules rules.json

    {skill_root} = 이 스킬이 설치된 디렉토리 (일반적으로 ~/.claude/skills/publish-agent;
    리포에서 직접 쓸 때는 <repo>/skills). Windows에서는 python3 대신 py -3 사용.

모듈:
    verify(draft_text: str, fp: dict, rules: dict) -> dict
"""

import argparse
import json
import sys
from pathlib import Path

from sermon_fingerprint import fingerprint, split_sentences

# ---------------------------------------------------------------------------
# 기본 AI 상투구 목록 (rules.json의 ai_tells로 가감 가능)
# ---------------------------------------------------------------------------

DEFAULT_AI_TELLS = [
    "결론부터 말씀드리면",
    "요약하자면",
    "다음과 같습니다",
    "라고 할 수 있습니다",
    "이번 시간에는",
    "함께 살펴보겠습니다",
    "마무리하겠습니다",
]

# band 이름 -> fingerprint 실측치 조회 함수
_BAND_GETTERS = {
    "sent_p50": lambda fp: fp["sent_words"]["p50"],
    "ending_family_share": lambda fp: (
        fp["endings"].get("습니다", 0.0) + fp["endings"].get("ㅂ니다", 0.0)
    ),
    "question_per_1k": lambda fp: fp["punct_per_1k"]["question"],
    "exclam_per_1k": lambda fp: fp["punct_per_1k"]["exclam"],
}


def _find_evidence_sentence(text, needle, sents=None):
    """Return the first sentence containing needle, or a text snippet fallback."""
    if sents is None:
        sents = split_sentences(text)
    for s in sents:
        if needle in s:
            return s
    idx = text.find(needle)
    if idx == -1:
        return needle
    start = max(0, idx - 20)
    end = min(len(text), idx + len(needle) + 20)
    return text[start:end].strip()


def _check_bands(draft_fp, rules, sents):
    violations = []
    bands = rules.get("bands")
    if not bands:
        return violations
    for name, bounds in bands.items():
        getter = _BAND_GETTERS.get(name)
        if getter is None:
            continue
        lo, hi = bounds[0], bounds[1]
        actual = getter(draft_fp)
        if actual < lo or actual > hi:
            evidence = sents[0] if sents else ""
            violations.append(
                {
                    "check": "bands",
                    "expected": f"[{lo}, {hi}]",
                    "actual": actual,
                    "evidence": f"{name}={actual}; first sentence: {evidence}",
                }
            )
    return violations


def _check_must_zero(draft_text, rules, sents):
    violations = []
    for phrase in rules.get("must_zero", []):
        if phrase in draft_text:
            violations.append(
                {
                    "check": "must_zero",
                    "expected": phrase,
                    "actual": "found",
                    "evidence": _find_evidence_sentence(draft_text, phrase, sents),
                }
            )
    return violations


def _check_ai_tells(draft_text, rules, sents):
    violations = []
    tells = list(DEFAULT_AI_TELLS) + list(rules.get("ai_tells", []))
    for phrase in tells:
        if phrase in draft_text:
            violations.append(
                {
                    "check": "ai_tells",
                    "expected": phrase,
                    "actual": "found",
                    "evidence": _find_evidence_sentence(draft_text, phrase, sents),
                }
            )
    return violations


def _check_signatures(draft_text, rules):
    violations = []
    for sig in rules.get("signatures", []):
        expr = sig["expr"]
        min_per_doc = sig["min_per_doc"]
        actual = draft_text.count(expr)
        if actual < min_per_doc:
            violations.append(
                {
                    "check": "signatures",
                    "expected": f"min_per_doc={min_per_doc} for '{expr}'",
                    "actual": actual,
                    "evidence": f"'{expr}' found {actual} time(s), expected >= {min_per_doc}",
                }
            )
    return violations


def verify(draft_text, fp, rules):
    """Verify a sermon draft against a fingerprint and rules, returning
    {"ok": bool, "violations": [...]}."""
    draft_fp = fingerprint([draft_text])
    sents = split_sentences(draft_text)

    violations = []
    violations.extend(_check_bands(draft_fp, rules, sents))
    violations.extend(_check_must_zero(draft_text, rules, sents))
    violations.extend(_check_ai_tells(draft_text, rules, sents))
    violations.extend(_check_signatures(draft_text, rules))

    return {"ok": len(violations) == 0, "violations": violations}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Verify a sermon draft against a fingerprint and rules gate."
    )
    parser.add_argument("draft", help="Path to draft .md/.txt file")
    parser.add_argument("--fingerprint", required=True, help="Path to fingerprint JSON")
    parser.add_argument("--rules", required=True, help="Path to rules.json")
    args = parser.parse_args(argv)

    draft_text = Path(args.draft).read_text(encoding="utf-8")
    fp = json.loads(Path(args.fingerprint).read_text(encoding="utf-8"))
    rules = json.loads(Path(args.rules).read_text(encoding="utf-8"))

    result = verify(draft_text, fp, rules)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
