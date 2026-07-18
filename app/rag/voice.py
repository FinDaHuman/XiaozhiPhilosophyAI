"""Utilities for answers that will be read aloud by the XiaoZhi robot."""

import re


SPOKEN_DAC_BRAND = "Đông Anh Capital"
SPOKEN_DAC_DOMAIN = "Đông Anh Capital chấm com"
_DAC_QUESTION_MARKERS = (
    "đông anh capital",
    "hiro",
)


def normalize_dac_pronunciation(text: str) -> str:
    """Use an unambiguous Vietnamese spelling for DAC text sent to TTS."""
    text = re.sub(
        r"\b(?:https?://)?(?:www\.)?donganhcapital\.com\b(?:/[^\s.,;:!?)]*)?",
        SPOKEN_DAC_DOMAIN,
        text,
        flags=re.IGNORECASE,
    )
    return re.sub(
        r"\b(?:dong|đông)\s*anh\s*capital\b",
        SPOKEN_DAC_BRAND,
        text,
        flags=re.IGNORECASE,
    )


def enforce_voice_source_for_question(answer: str, question: str) -> str:
    """Correct impossible spoken citations for questions about DAC or Hiro."""
    normalized_question = normalize_dac_pronunciation(question).lower()
    if not any(marker in normalized_question for marker in _DAC_QUESTION_MARKERS):
        return answer

    def replacement(match: re.Match) -> str:
        prefix = "Theo" if match.group(0)[:1].isupper() else "theo"
        return f"{prefix} tài liệu {SPOKEN_DAC_BRAND}"

    return re.sub(
        r"\btheo\s+(?:slide(?:\s+kinh tế chính trị|\s+KTCT)?\s+\d+|giáo trình)\b",
        replacement,
        answer,
        flags=re.IGNORECASE,
    )


def dedupe_voice_sources(answer: str) -> str:
    """Mention each spoken source at most once in a short robot answer."""
    pattern = re.compile(
        r"\btheo\s+(?:tài liệu Đông Anh Capital|slide(?: kinh tế chính trị)? \d+|giáo trình)\b(?:,\s*)?",
        flags=re.IGNORECASE,
    )
    seen = set()

    def replacement(match: re.Match) -> str:
        key = match.group(0).rstrip(", \t\r\n").lower()
        if key in seen:
            return ""
        seen.add(key)
        return match.group(0)

    answer = pattern.sub(replacement, answer)
    answer = re.sub(r",\s*([.!?])", r"\1", answer)
    answer = re.sub(r"([.!?])\s*,\s*", r"\1 ", answer)
    answer = re.sub(r"\s{2,}", " ", answer)
    return answer.strip()


def finalize_voice_answer(answer: str, question: str) -> str:
    """Apply the complete deterministic contract for a generated robot answer."""
    answer = sanitize_voice_answer(answer)
    answer = enforce_voice_source_for_question(answer, question)
    return dedupe_voice_sources(answer)


def sanitize_voice_answer(answer: str) -> str:
    """Convert written citations/formatting into text that is safe for TTS."""
    spoken_citations = (
        (r"(?:theo\s*)?\[\s*DongAnhCapital\s*\]", "theo tài liệu Đông Anh Capital"),
        (
            r"(?:theo\s*)?\[\s*Slide\s+KTCT\s+(\d+)\s*\]",
            r"theo slide kinh tế chính trị \1",
        ),
        (r"(?:theo\s*)?\[\s*Slide\s+(\d+)\s*\]", r"theo slide \1"),
        (r"(?:theo\s*)?\[\s*Giáo trình\s*\]", "theo giáo trình"),
    )
    for pattern, replacement in spoken_citations:
        answer = re.sub(pattern, replacement, answer, flags=re.IGNORECASE)

    answer = re.sub(
        r"\btheo\s+theo\s+(?=tài liệu|slide|giáo trình)",
        "theo ",
        answer,
        flags=re.IGNORECASE,
    )
    answer = re.sub(
        r"\btheo\s+DongAnhCapital\b",
        "theo tài liệu Đông Anh Capital",
        answer,
        flags=re.IGNORECASE,
    )
    answer = re.sub(r"(?m)^\s*[-*•]\s+", "", answer)
    answer = answer.replace("**", "").replace("__", "").replace("`", "")
    answer = re.sub(r"\[([^\[\]]+)\]", r"\1", answer)
    answer = re.sub(r"\s+", " ", answer).strip()
    answer = re.sub(
        r"([.!?])\s+theo\s+"
        r"(tài liệu (?:DongAnh|Đông Anh) Capital|slide(?: kinh tế chính trị)? \d+|giáo trình)"
        r"[.!?]?$",
        r" theo \2\1",
        answer,
        flags=re.IGNORECASE,
    )
    answer = normalize_dac_pronunciation(answer)
    return answer[:1].upper() + answer[1:] if answer else answer
