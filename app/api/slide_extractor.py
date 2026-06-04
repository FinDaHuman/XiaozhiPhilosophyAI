"""
Slide Extractor — Extracts individual PDF pages as PNG images.

Uses PyMuPDF (fitz) to render pages from the Slide.pdf file and cache
them as PNG images in the webcontent/slides/ directory.
"""

import os
import logging
from pathlib import Path

import fitz  # PyMuPDF

logger = logging.getLogger("SLIDE_EXTRACTOR")

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PDF_PATH = BASE_DIR / "webcontent" / "Slide.pdf"
SLIDES_DIR = BASE_DIR / "webcontent" / "slides"


def ensure_slides_dir():
    """Ensure the slides output directory exists."""
    SLIDES_DIR.mkdir(parents=True, exist_ok=True)


def get_slide_image_path(page_num: int) -> Path:
    """Get the cached image path for a given page number (1-indexed)."""
    return SLIDES_DIR / f"slide_{page_num:03d}.png"


def extract_slide(page_num: int, dpi: int = 200) -> Path | None:
    """
    Extract a single PDF page as a PNG image.

    Args:
        page_num: Page number (1-indexed as per ChiaSlide.txt)
        dpi: Resolution for rendering (default 200 for good quality)

    Returns:
        Path to the cached PNG image, or None if extraction failed.
    """
    ensure_slides_dir()
    out_path = get_slide_image_path(page_num)

    # Return cached version if it exists
    if out_path.exists():
        return out_path

    if not PDF_PATH.exists():
        logger.error("PDF not found: %s", PDF_PATH)
        return None

    try:
        doc = fitz.open(str(PDF_PATH))
        # PDF pages are 0-indexed, but ChiaSlide uses 1-indexed
        page_index = page_num - 1

        if page_index < 0 or page_index >= len(doc):
            logger.error("Page %d out of range (total pages: %d)", page_num, len(doc))
            doc.close()
            return None

        page = doc[page_index]
        # Render at specified DPI
        zoom = dpi / 72  # 72 is the default PDF DPI
        matrix = fitz.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=matrix)
        pixmap.save(str(out_path))
        doc.close()

        logger.info("Extracted slide %d → %s", page_num, out_path.name)
        return out_path

    except Exception as exc:
        logger.exception("Failed to extract slide %d: %s", page_num, exc)
        return None


def extract_all_lesson_slides() -> dict[int, list[Path]]:
    """
    Pre-extract all slide images referenced in ChiaSlide.txt.

    Returns:
        Dictionary mapping lesson number to list of slide image paths.
    """
    lessons = parse_chia_slide()
    result = {}

    for lesson_num, info in lessons.items():
        paths = []
        for page_num in info["pages"]:
            path = extract_slide(page_num)
            if path:
                paths.append(path)
        result[lesson_num] = paths
        logger.info(
            "Lesson %d (%s): extracted %d/%d slides",
            lesson_num, info["title"], len(paths), len(info["pages"]),
        )

    return result


def parse_chia_slide() -> dict:
    """
    Parse ChiaSlide.txt to get lesson structure.

    Returns:
        Dictionary: {lesson_num: {"pages": [int], "title": str}}
    """
    chia_path = BASE_DIR / "webcontent" / "ChiaSlide.txt"
    lessons = {}

    if not chia_path.exists():
        logger.error("ChiaSlide.txt not found: %s", chia_path)
        return lessons

    with open(chia_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            # Format: "4,5,6 - Giới thiệu"
            parts = line.split(" - ", 1)
            if len(parts) != 2:
                continue

            page_str, title = parts
            pages = [int(p.strip()) for p in page_str.split(",")]
            lessons[i] = {"pages": pages, "title": title.strip()}

    return lessons


def get_lessons_json() -> list[dict]:
    """
    Get lesson data as JSON-serializable list.

    Returns:
        List of lesson dicts with keys: number, title, pages, slide_urls
    """
    lessons = parse_chia_slide()
    result = []

    for num, info in lessons.items():
        slide_urls = [f"/api/slides/{p}" for p in info["pages"]]
        result.append({
            "number": num,
            "title": info["title"],
            "pages": info["pages"],
            "slide_urls": slide_urls,
        })

    return result
