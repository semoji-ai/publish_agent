import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "shared" / "scripts"))

from sermon_fingerprint import fingerprint, load_corpus  # noqa: E402
from verify_sermon import DEFAULT_AI_TELLS, verify  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures"
CORPUS = FIXTURES / "corpus"


@pytest.fixture(scope="module")
def fp():
    return fingerprint(load_corpus(CORPUS))


@pytest.fixture(scope="module")
def rules():
    return json.loads((FIXTURES / "rules.json").read_text(encoding="utf-8"))


COMPLIANT_DRAFT = """\
사랑하는 성도 여러분, 오늘 우리는 마가복음 말씀을 함께 나누고자 합니다.
하나님은 우리를 향한 크신 계획을 가지고 계십니다.
첫째, 하나님의 계획은 선한 계획입니다.
둘째, 하나님의 계획은 신실한 계획입니다.
저는 이 말씀을 묵상하면서 큰 은혜를 받았습니다.
그러나 우리는 그 계획을 자주 의심하며 살아갑니다.
사랑하는 성도 여러분, 우리도 이 믿음을 굳게 붙잡아야 합니다.
바울은 빌립보서에서 이렇게 고백했습니다(빌 1:6).
우리 함께 이 말씀을 마음에 새기며 살아갑시다.
하나님께서 우리와 늘 함께하십니다.
"""

BAND_VIOLATING_DRAFT = """\
사랑하는 성도 여러분, 안녕하세요? 오늘 정말 좋은 날씨죠?
저는 요즘 너무 바빴어요. 그래서 준비를 많이 못했어요!
그래도 여러분과 함께해서 정말 기뻐요! 너무 좋아요!
오늘 이야기는 짧게 할게요! 재밌게 들어주세요!
다음에 또 만나요! 안녕히 가세요!
"""

MUST_ZERO_DRAFT = """\
사랑하는 성도 여러분, 오늘 말씀을 시작하겠습니다.
결론부터 말씀드리면 하나님은 우리를 사랑하십니다.
저는 이 말씀을 묵상하면서 큰 은혜를 받았습니다.
그러나 우리는 이 사랑을 자주 잊어버립니다.
첫째, 하나님의 사랑은 크십니다.
"""

AI_TELL_DRAFT = """\
사랑하는 성도 여러분, 오늘 말씀을 시작하겠습니다.
오늘의 핵심은 하나님의 은혜입니다.
저는 이 말씀을 묵상하면서 큰 은혜를 받았습니다.
그러나 우리는 이 은혜를 자주 잊어버립니다.
첫째, 하나님의 은혜는 값없이 주어집니다.
"""

SIGNATURE_SHORTFALL_DRAFT = """\
오늘 우리는 마가복음 말씀을 함께 나누고자 합니다.
하나님은 우리를 향한 크신 계획을 가지고 계십니다.
첫째, 하나님의 계획은 선한 계획입니다.
둘째, 하나님의 계획은 신실한 계획입니다.
저는 이 말씀을 묵상하면서 큰 은혜를 받았습니다.
그러나 우리는 그 계획을 자주 의심하며 살아갑니다.
바울은 빌립보서에서 이렇게 고백했습니다(빌 1:6).
우리 함께 이 말씀을 마음에 새기며 살아갑시다.
하나님께서 우리와 늘 함께하십니다.
"""


def test_compliant_draft_passes(fp, rules):
    result = verify(COMPLIANT_DRAFT, fp, rules)
    assert result["ok"] is True
    assert result["violations"] == []


def test_band_violation_detected_with_evidence(fp, rules):
    result = verify(BAND_VIOLATING_DRAFT, fp, rules)
    assert result["ok"] is False
    band_violations = [v for v in result["violations"] if v["check"] == "bands"]
    assert band_violations, "expected at least one band violation"
    for v in band_violations:
        assert "expected" in v and "actual" in v
        assert "evidence" in v


def test_must_zero_detected_with_containing_sentence_as_evidence(fp, rules):
    result = verify(MUST_ZERO_DRAFT, fp, rules)
    assert result["ok"] is False
    must_zero_violations = [v for v in result["violations"] if v["check"] == "must_zero"]
    assert len(must_zero_violations) == 1
    v = must_zero_violations[0]
    assert v["expected"] == "결론부터 말씀드리면"
    assert "결론부터 말씀드리면" in v["evidence"]


def test_ai_tell_extra_from_rules_detected(fp, rules):
    result = verify(AI_TELL_DRAFT, fp, rules)
    assert result["ok"] is False
    tell_violations = [v for v in result["violations"] if v["check"] == "ai_tells"]
    assert any("오늘의 핵심은" in v["evidence"] for v in tell_violations)


def test_builtin_ai_tell_detected_without_rules_entry(fp, rules):
    draft = "사랑하는 성도 여러분, 요약하자면 하나님은 우리를 사랑하십니다.\n"
    result = verify(draft, fp, rules)
    tell_violations = [v for v in result["violations"] if v["check"] == "ai_tells"]
    assert any("요약하자면" in v["evidence"] for v in tell_violations)


def test_signature_shortfall_detected(fp, rules):
    result = verify(SIGNATURE_SHORTFALL_DRAFT, fp, rules)
    assert result["ok"] is False
    sig_violations = [v for v in result["violations"] if v["check"] == "signatures"]
    assert len(sig_violations) == 1
    assert sig_violations[0]["expected"] == "min_per_doc=1 for '사랑하는 성도 여러분'"
    assert sig_violations[0]["actual"] == 0


def test_partial_rules_skip_absent_sections(fp):
    partial_rules = {"must_zero": ["결론부터 말씀드리면"]}
    # No bands/signatures/ai_tells keys -> those checks should simply be skipped.
    result = verify(BAND_VIOLATING_DRAFT, fp, partial_rules)
    checks_run = {v["check"] for v in result["violations"]}
    assert "bands" not in checks_run
    assert "signatures" not in checks_run
    # must_zero absent from this draft, ai_tells default list still applies
    assert result["ok"] in (True, False)  # should not raise; sanity check only


def test_default_ai_tells_list_has_required_entries():
    required = {
        "결론부터 말씀드리면",
        "요약하자면",
        "다음과 같습니다",
        "라고 할 수 있습니다",
        "이번 시간에는",
        "함께 살펴보겠습니다",
        "마무리하겠습니다",
    }
    assert required.issubset(set(DEFAULT_AI_TELLS))
