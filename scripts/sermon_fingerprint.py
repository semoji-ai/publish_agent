#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sermon_fingerprint.py — 설교 코퍼스 정량 문체 지표 (stdlib only, Python 3.9+)

형태소 분석기 없이 정규식 기반으로 근사 측정한다 (gn-voice fingerprint.py와
동일한 접근을 형태소 분석기 없이 단순화).

CLI:
    python3 scripts/sermon_fingerprint.py <corpus_dir> [-o out.json]

모듈:
    fingerprint(texts: list[str]) -> dict
"""

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 문장 분리
# ---------------------------------------------------------------------------

# 장절 표기 괄호 보호용 마스크 토큰 (문장 분리 전에 내부 공백/구두점을 숨김)
_VERSE_REF_RE = re.compile(r"\([^()]*\d+[:：]\d+[^()]*\)")
_MASK_PREFIX = "VERSEREF"
_SENT_SPLIT_RE = re.compile(r"(?<=[.!?…])\s+")


def _mask_verse_refs(text):
    refs = []

    def _sub(m):
        refs.append(m.group(0))
        return f"{_MASK_PREFIX}{len(refs) - 1}"

    masked = _VERSE_REF_RE.sub(_sub, text)
    return masked, refs


def _unmask_verse_refs(text, refs):
    def _sub(m):
        idx = int(m.group(1))
        return refs[idx]

    return re.sub(f"{_MASK_PREFIX}(\\d+)", _sub, text)


def split_sentences(text):
    """Split text into sentences, protecting verse refs like (요 3:16)."""
    masked, refs = _mask_verse_refs(text)
    raw_sents = _SENT_SPLIT_RE.split(masked)
    sents = []
    for s in raw_sents:
        s = _unmask_verse_refs(s, refs).strip()
        if s:
            sents.append(s)
    return sents


def split_paragraphs(text):
    """Split text into paragraphs on blank lines."""
    return [p for p in re.split(r"\n\s*\n", text)]


# ---------------------------------------------------------------------------
# 어미 패턴 (문장 끝 어절 대상)
# ---------------------------------------------------------------------------

ENDING_PATTERNS = [
    ("습니다", re.compile(r"습니다[.!?…]*$")),
    ("ㅂ니다", re.compile(r"[가-힣]*(?<!습)니다[.!?…]*$")),
    ("아요/어요", re.compile(r"(아요|어요|여요)[.!?…]*$")),
    ("죠", re.compile(r"죠[.!?…]*$")),
    ("니까/까", re.compile(r"(니까|까요|까)[.!?…]*$")),
    ("십시오", re.compile(r"(십시오|세요|셔요)[.!?…]*$")),
    ("ㅂ시다", re.compile(r"[가-힣]*[가-힣]시다[.!?…]*$")),
    ("으라/라", re.compile(r"(으라|어라|아라|거라|너라)[.!?…]*$")),
    ("다(평서)", re.compile(r"[가-힣]다[.!?…]*$")),
]


_TRAILING_BIBLE_REF_RE = re.compile(r"\([^()]*\)\s*[.!?…]*$")


def _last_word(sentence):
    # Strip a trailing verse-ref parenthetical like "(요 3:16)" so it doesn't
    # swallow the preceding word's ending (the ref may contain a space).
    trailing_punct = ""
    m = re.search(r"[.!?…]+$", sentence.strip())
    if m:
        trailing_punct = m.group(0)
    stripped = _TRAILING_BIBLE_REF_RE.sub("", sentence.strip()).strip()
    if stripped:
        tokens = (stripped + trailing_punct).split()
    else:
        tokens = sentence.strip().split()
    return tokens[-1] if tokens else ""


def classify_ending(sentence):
    word = _last_word(sentence)
    if not word:
        return "_other"
    for name, pattern in ENDING_PATTERNS:
        if pattern.search(word):
            return name
    return "_other"


# ---------------------------------------------------------------------------
# 담화 마커 / 자기지칭 / 성경 인용
# ---------------------------------------------------------------------------

ORDINAL_RE = re.compile(r"(첫째|둘째|셋째|넷째|다섯째|마지막으로|끝으로)")
ADVERSATIVE_RE = re.compile(r"(그러나|하지만|그런데|그렇지만)")
VOCATIVE_RE = re.compile(r"(사랑하는\s*[가-힣]*\s*여러분|성도\s*여러분|형제자매\s*여러분|교우\s*여러분)")
SELF_REF_RE = re.compile(r"(저는|제가|저희|나는|내가|우리는|우리가)")
BIBLE_REF_RE = re.compile(r"(\([가-힣]{1,4}\s*\d+[:：]\d+[-~]?\d*\)|「[^」]*」|『[^』]*』)")

PUNCT_PATTERNS = {
    "period": re.compile(r"\."),
    "comma": re.compile(r","),
    "question": re.compile(r"\?"),
    "exclam": re.compile(r"!"),
    "ellipsis": re.compile(r"…|\.\.\."),
    "quote": re.compile(r"[\"'“”‘’「」『』]"),
}


# ---------------------------------------------------------------------------
# 백분위 (n<20에서도 안전)
# ---------------------------------------------------------------------------

def _percentile(sorted_values, pct):
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    k = (len(sorted_values) - 1) * (pct / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_values) - 1)
    if f == c:
        return float(sorted_values[f])
    d0 = sorted_values[f] * (c - k)
    d1 = sorted_values[c] * (k - f)
    return float(d0 + d1)


def _percentiles(values):
    if not values:
        return {"p10": 0.0, "p50": 0.0, "p90": 0.0, "mean": 0.0}
    sorted_values = sorted(values)
    return {
        "p10": _percentile(sorted_values, 10),
        "p50": _percentile(sorted_values, 50),
        "p90": _percentile(sorted_values, 90),
        "mean": statistics.mean(values),
    }


# ---------------------------------------------------------------------------
# 코퍼스 로딩
# ---------------------------------------------------------------------------

def load_corpus(corpus_dir):
    """Load all .md/.txt files (recursively) from corpus_dir as UTF-8 text.

    Raises SystemExit with a clear message if the folder is missing or
    contains no usable documents.
    """
    corpus_path = Path(corpus_dir)
    if not corpus_path.exists() or not corpus_path.is_dir():
        raise SystemExit(f"corpus_dir not found or not a directory: {corpus_dir}")

    paths = sorted(
        p for p in corpus_path.rglob("*") if p.suffix.lower() in (".md", ".txt") and p.is_file()
    )
    if not paths:
        raise SystemExit(f"no .md/.txt files found in corpus_dir: {corpus_dir}")

    texts = []
    for p in paths:
        content = p.read_text(encoding="utf-8").strip()
        if content:
            texts.append(content)

    if not texts:
        raise SystemExit(f"corpus_dir contains only empty files: {corpus_dir}")

    return texts


# ---------------------------------------------------------------------------
# fingerprint 본체
# ---------------------------------------------------------------------------

def fingerprint(texts):
    """Compute style fingerprint metrics for a list of raw document texts."""
    if not texts:
        raise ValueError("texts must be a non-empty list of documents")

    n_docs = len(texts)

    all_sents = []
    para_sent_counts = []
    blank_line_total = 0
    line_total = 0

    for text in texts:
        paragraphs = split_paragraphs(text)
        for para in paragraphs:
            sents = split_sentences(para)
            if sents:
                para_sent_counts.append(len(sents))
            all_sents.extend(sents)

        lines = text.split("\n")
        line_total += len(lines)
        blank_line_total += sum(1 for ln in lines if not ln.strip())

    n_sents = len(all_sents)

    sent_word_counts = [len(s.split()) for s in all_sents]
    endings_counter = {}
    for s in all_sents:
        pattern = classify_ending(s)
        endings_counter[pattern] = endings_counter.get(pattern, 0) + 1
    endings = {
        k: (v / n_sents if n_sents else 0.0) for k, v in endings_counter.items()
    }

    total_chars = sum(len(t) for t in texts)
    total_words = sum(len(t.split()) for t in texts)

    punct_per_1k = {}
    for name, pattern in PUNCT_PATTERNS.items():
        count = sum(len(pattern.findall(t)) for t in texts)
        punct_per_1k[name] = (count / total_chars * 1000) if total_chars else 0.0

    def _marker_rate(pattern):
        count = sum(len(pattern.findall(t)) for t in texts)
        return (count / total_words * 1000) if total_words else 0.0

    markers_per_1k_words = {
        "ordinal": _marker_rate(ORDINAL_RE),
        "adversative": _marker_rate(ADVERSATIVE_RE),
        "vocative": _marker_rate(VOCATIVE_RE),
    }

    self_ref_per_1k_words = _marker_rate(SELF_REF_RE)

    bible_ref_count = sum(len(BIBLE_REF_RE.findall(t)) for t in texts)
    bible_refs_per_1k_chars = (bible_ref_count / total_chars * 1000) if total_chars else 0.0

    para_sents_p50 = _percentile(sorted(para_sent_counts), 50) if para_sent_counts else 0.0
    blank_ratio = (blank_line_total / line_total) if line_total else 0.0

    return {
        "n_docs": n_docs,
        "n_sents": n_sents,
        "sent_words": _percentiles(sent_word_counts),
        "endings": endings,
        "punct_per_1k": punct_per_1k,
        "markers_per_1k_words": markers_per_1k_words,
        "self_ref_per_1k_words": self_ref_per_1k_words,
        "bible_refs_per_1k_chars": bible_refs_per_1k_chars,
        "para": {
            "sents_p50": para_sents_p50,
            "blank_ratio": blank_ratio,
        },
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Compute a corpus style fingerprint for Korean sermon texts."
    )
    parser.add_argument("corpus_dir", help="Directory of .md/.txt sermon files")
    parser.add_argument("-o", "--output", help="Path to write JSON output (default: stdout)")
    args = parser.parse_args(argv)

    texts = load_corpus(args.corpus_dir)
    result = fingerprint(texts)

    output_json = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(output_json, encoding="utf-8")
        print(f"wrote fingerprint to {args.output}", file=sys.stderr)
    else:
        print(output_json)

    return 0


if __name__ == "__main__":
    sys.exit(main())
