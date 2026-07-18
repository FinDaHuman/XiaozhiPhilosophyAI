"""Utilities for answers that will be read aloud by the XiaoZhi robot."""

import re


def sanitize_voice_answer(answer: str) -> str:
    """Convert written citations/formatting into text that is safe for TTS."""
    spoken_citations = (
        (r"(?:theo\s*)?\[\s*DongAnhCapital\s*\]", "theo tài liệu DongAnh Capital"),
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
        "theo tài liệu DongAnh Capital",
        answer,
        flags=re.IGNORECASE,
    )
    answer = re.sub(r"(?m)^\s*[-*•]\s+", "", answer)
    answer = answer.replace("**", "").replace("__", "").replace("`", "")
    answer = re.sub(r"\[([^\[\]]+)\]", r"\1", answer)
    answer = re.sub(r"\s+", " ", answer).strip()
    answer = re.sub(
        r"([.!?])\s+theo\s+"
        r"(tài liệu DongAnh Capital|slide(?: kinh tế chính trị)? \d+|giáo trình)"
        r"[.!?]?$",
        r" theo \2\1",
        answer,
        flags=re.IGNORECASE,
    )
    return answer[:1].upper() + answer[1:] if answer else answer
