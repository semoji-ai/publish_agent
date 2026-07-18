import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "shared" / "scripts"))

from sermon_fingerprint import classify_ending, fingerprint, load_corpus  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "corpus"


def _load_texts(dir_path):
    return load_corpus(dir_path)


@pytest.fixture(scope="module")
def fp():
    texts = _load_texts(FIXTURES)
    return fingerprint(texts)


def test_n_docs(fp):
    assert fp["n_docs"] == 3


def test_n_sents_positive(fp):
    assert fp["n_sents"] > 30


def test_sent_words_p50_in_expected_range(fp):
    # Korean sermon sentences (어절 count) typically land roughly 5-15 words.
    p50 = fp["sent_words"]["p50"]
    assert 4 <= p50 <= 16


def test_sent_words_has_all_percentile_keys(fp):
    for key in ("p10", "p50", "p90", "mean"):
        assert key in fp["sent_words"]


def test_endings_top_pattern_is_seumnida_family(fp):
    # The 습니다/ㅂ니다 family together (경어체 설교체) should dominate the
    # fixture set, which is 2 경어체 sermons + 1 반말 sermon.
    endings = fp["endings"]
    assert endings, "endings dict should not be empty"
    seumnida_family = endings.get("습니다", 0.0) + endings.get("ㅂ니다", 0.0)
    other_buckets = {k: v for k, v in endings.items() if k not in ("습니다", "ㅂ니다")}
    max_other = max(other_buckets.values()) if other_buckets else 0.0
    assert seumnida_family > max_other
    assert seumnida_family >= 0.3


def test_vocative_marker_present(fp):
    assert fp["markers_per_1k_words"]["vocative"] > 0


def test_ordinal_marker_present(fp):
    assert fp["markers_per_1k_words"]["ordinal"] > 0


def test_adversative_marker_present(fp):
    assert fp["markers_per_1k_words"]["adversative"] > 0


def test_bible_refs_per_1k_chars_positive(fp):
    assert fp["bible_refs_per_1k_chars"] > 0


def test_self_ref_per_1k_words_positive(fp):
    assert fp["self_ref_per_1k_words"] > 0


def test_punct_per_1k_keys(fp):
    for key in ("period", "comma", "question", "exclam", "ellipsis", "quote"):
        assert key in fp["punct_per_1k"]


def test_para_keys(fp):
    assert "sents_p50" in fp["para"]
    assert "blank_ratio" in fp["para"]


def test_empty_folder_raises_clear_error(tmp_path):
    empty_dir = tmp_path / "empty_corpus"
    empty_dir.mkdir()
    with pytest.raises((SystemExit, ValueError)):
        load_corpus(empty_dir)


def test_missing_folder_raises_clear_error(tmp_path):
    missing_dir = tmp_path / "does_not_exist"
    with pytest.raises((SystemExit, ValueError)):
        load_corpus(missing_dir)


def test_verse_ref_does_not_split_sentence():
    # Sentence with a verse ref like (요 3:16) should not be split at the
    # internal period.
    from sermon_fingerprint import split_sentences

    text = "하나님은 세상을 이처럼 사랑하셨습니다(요 3:16). 그러나 우리는 잊고 삽니다."
    sents = split_sentences(text)
    assert len(sents) == 2
    assert "(요 3:16)" in sents[0]


def test_honorific_bnida_classified():
    assert classify_ending("하나님께서 우리와 늘 함께하십니다.") == "ㅂ니다"
    assert classify_ending("우리는 오늘도 갑니다.") == "ㅂ니다"
    assert classify_ending("말씀을 봅니다.") == "ㅂ니다"
    assert classify_ending("우리는 믿습니다.") == "습니다"


def test_cheongyu_bsida_classified():
    assert classify_ending("우리 함께 나눕시다.") == "ㅂ시다"
    assert classify_ending("함께 갑시다.") == "ㅂ시다"


def test_sipsio_not_bsida():
    assert classify_ending("말씀을 붙드십시오.") == "십시오"
