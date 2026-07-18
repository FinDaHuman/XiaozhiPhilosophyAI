"""Query routing rules for the presentation knowledge base."""

import unicodedata

DAC_SOURCE = "DongAnhCapital_KnowledgeBase.md"

DAC_QUERY_MARKERS = (
    "dong anh capital",
    "donganh capital",
    "donganhcapital",
    "hiro",
    "ma co phieu",
    "tu van sau",
)

KTCT_QUERY_MARKERS = (
    "kinh te chinh tri",
    "canh tranh",
    "doc quyen",
    "tu ban tai chinh",
    "xuat khau tu ban",
    "vai tro lich su cua chu nghia tu ban",
)

MLN111_QUERY_MARKERS = (
    "mln111",
    "triet hoc",
    "mau thuan bien chung",
    "mat doi lap",
    "vat chat",
    "y thuc",
    "phep bien chung",
)


def _fold_vietnamese(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold())
    ascii_like = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    return ascii_like.replace("đ", "d").strip()


def classify_query_domain(query: str) -> str:
    """Choose the only knowledge domain that should answer a query.

    Đông Anh Capital is the presentation's active subject, so an ambiguous
    query belongs to DAC. Legacy course material is selected only by an
    explicit subject marker.
    """
    normalized = _fold_vietnamese(query)
    if any(marker in normalized for marker in DAC_QUERY_MARKERS):
        return "dac"
    if any(marker in normalized for marker in KTCT_QUERY_MARKERS):
        return "ktct"
    if any(marker in normalized for marker in MLN111_QUERY_MARKERS):
        return "mln111"
    return "dac"


def source_domain(source: str) -> str:
    """Classify an indexed source without depending on a specific backend."""
    normalized = source.casefold().replace("_", "").replace(" ", "")
    if "donganhcapital" in normalized:
        return "dac"
    if "slidektct" in normalized or "kinhtechinhtri" in normalized:
        return "ktct"
    if "slide" in normalized or "triethoc" in normalized:
        return "mln111"
    return "other"
