"""E2E: fixture corpus -> fingerprint -> in-test rules -> verify.

Exercises the full pipeline described in docs/specs/2026-07-18-sermon-pack-design.md
end to end using stdlib only. Rules are built from the *measured* fingerprint
(bands = measured value +/- 20%), matching how /publish-profile is expected to
derive sermon-rules.json from sermon-fingerprint.json.

Uses a dedicated in-test formal-register corpus (rather than
tests/fixtures/corpus, which intentionally mixes in an informal/반말 document
for tests/test_verify.py's band-violation coverage) so the derived bands
reflect a single consistent register, matching the single-author assumption
behind sermon-pack.md/sermon-rules.json.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sermon_fingerprint import fingerprint  # noqa: E402
from verify_sermon import verify  # noqa: E402

CORPUS_TEXTS = [
    """\
사랑하는 성도 여러분, 오늘 우리는 요한복음 말씀을 함께 나누고자 합니다.
하나님은 세상을 이처럼 사랑하셨습니다(요 3:16).
그러나 우리는 그 사랑을 자주 잊어버리고 살아갑니다.
저는 이 말씀을 묵상하면서 큰 은혜를 받았습니다.
첫째, 하나님의 사랑은 조건이 없는 사랑입니다.
둘째, 하나님의 사랑은 희생하는 사랑입니다.
셋째, 하나님의 사랑은 영원한 사랑입니다.
사랑하는 성도 여러분, 우리도 이런 사랑을 실천해야 합니다.
바울은 로마서에서 이렇게 고백했습니다(롬 8:38).
그런데 우리는 여전히 두려움 속에서 살아갑니다.
저는 여러분이 이 말씀을 붙잡기를 소망합니다.
우리 함께 이 사랑을 이웃에게 전합시다.
사랑하는 성도 여러분, 오늘도 은혜가 넘치기를 바랍니다.
믿음으로 살아가는 자는 결코 흔들리지 않습니다.
하나님께서 우리와 늘 함께하십니다.
이제 우리는 기도로 이 말씀을 마무리하겠습니다.
사랑하는 성도 여러분, 다 함께 일어서서 기도하십시오.
""",
    """\
사랑하는 성도 여러분, 오늘은 시편의 말씀으로 은혜를 나누고자 합니다.
여호와는 나의 목자시니 내게 부족함이 없으리로다(시 23:1).
그러나 우리는 종종 부족함을 느끼며 불안해합니다.
저는 이 말씀 앞에서 저 자신을 돌아보았습니다.
첫째, 우리는 목자 되신 하나님을 신뢰해야 합니다.
둘째, 우리는 푸른 초장으로 인도하시는 은혜를 기억해야 합니다.
셋째, 우리는 사망의 음침한 골짜기에서도 두려워하지 말아야 합니다.
사랑하는 성도 여러분, 이 시편은 우리에게 큰 위로가 됩니다.
바울도 빌립보서에서 이렇게 권면했습니다(빌 4:6).
그런데 우리는 여전히 염려하며 살아갑니다.
저는 여러분이 오늘 이 말씀으로 위로받기를 원합니다.
우리 함께 이 은혜를 기억하며 살아갑시다.
사랑하는 성도 여러분, 하나님의 신실하심을 찬양합시다.
믿음으로 나아가는 자는 결코 부끄러움을 당하지 않습니다.
하나님께서 우리의 걸음을 인도하십니다.
이제 우리는 찬양으로 이 예배를 마무리하겠습니다.
사랑하는 성도 여러분, 다 함께 손을 들고 찬양하십시오.
""",
]


@pytest.fixture(scope="module")
def fp():
    return fingerprint(CORPUS_TEXTS)


def _band(value, pct=0.2):
    """Band = measured value +/- 20% (spec default). For near-zero baseline
    metrics (e.g. a corpus with no question/exclamation marks), a strict
    +/-20% window would exclude 0 itself -- so the lower bound floors at 0
    and a small allowance keeps 0 inside the band."""
    lo = max(0.0, value * (1 - pct))
    hi = max(value * (1 + pct), 0.5)
    return [lo, hi]


@pytest.fixture(scope="module")
def rules(fp):
    ending_family_share = fp["endings"].get("습니다", 0.0) + fp["endings"].get("ㅂ니다", 0.0)
    return {
        "bands": {
            "sent_p50": _band(fp["sent_words"]["p50"]),
            "ending_family_share": _band(ending_family_share),
            "question_per_1k": _band(fp["punct_per_1k"]["question"]),
            "exclam_per_1k": _band(fp["punct_per_1k"]["exclam"]),
        },
        "must_zero": ["결론부터 말씀드리면"],
        "signatures": [{"expr": "사랑하는 성도 여러분", "min_per_doc": 1}],
        "ai_tells": [],
    }


# Compliant draft: same register/rhythm as the corpus (경어체, no AI 상투구,
# includes the required signature phrase) -- built from corpus-style sentences
# so its measured fingerprint lands inside the +/-20% bands derived above.
COMPLIANT_DRAFT = """\
사랑하는 성도 여러분, 오늘 본문 말씀을 함께 나누고자 합니다.
하나님은 우리를 향한 신실한 계획을 가지고 계십니다(엡 1:11).
그러나 우리는 이 계획을 자주 의심하며 살아갑니다.
저는 이 말씀을 묵상하면서 큰 위로를 받았습니다.
첫째, 그 계획은 선한 계획입니다.
둘째, 그 계획은 은혜로운 계획입니다.
셋째, 그 계획은 신실한 계획입니다.
사랑하는 성도 여러분, 오늘도 이 믿음을 굳게 붙잡읍시다.
바울은 빌립보서에서 이렇게 고백했습니다(빌 1:6).
그런데 우리는 여전히 조급하게 살아갑니다.
저는 여러분이 이 말씀으로 위로받기를 소망합니다.
우리 함께 이 은혜를 이웃에게 전합시다.
사랑하는 성도 여러분, 오늘도 평안이 넘치기를 바랍니다.
믿음으로 살아가는 자는 결코 흔들리지 않습니다.
하나님께서 우리와 늘 함께하십니다.
이제 우리는 기도로 이 예배를 마치고자 합니다.
사랑하는 성도 여러분, 다 함께 일어서서 기도하십시오.
"""

# Violating draft: 반말(informal endings, pulls ending_family_share off-band)
# + AI 상투구("결론부터 말씀드리면") + no required signature phrase +
# excessive question/exclamation marks (pushes punctuation bands off-range).
VIOLATING_DRAFT = """\
안녕? 오늘 진짜 좋은 날씨지?!
결론부터 말씀드리면 하나님은 우리를 사랑해!
나는 요즘 너무 바빴어! 그래서 준비를 많이 못했어?!
그래도 다들 만나서 정말 기뻐! 너무 좋아!?
다음에 또 보자! 안녕!
"""


def test_compliant_draft_passes_gate(fp, rules):
    result = verify(COMPLIANT_DRAFT, fp, rules)
    assert result["ok"] is True, result["violations"]
    assert result["violations"] == []


def test_violating_draft_fails_with_multiple_distinct_checks(fp, rules):
    result = verify(VIOLATING_DRAFT, fp, rules)
    assert result["ok"] is False
    checks = {v["check"] for v in result["violations"]}
    assert len(checks) >= 2, f"expected >=2 distinct check types, got {checks}"
    assert "must_zero" in checks
    assert "signatures" in checks
    for v in result["violations"]:
        assert "expected" in v and "actual" in v and "evidence" in v
