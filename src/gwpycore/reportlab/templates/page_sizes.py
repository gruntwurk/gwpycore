from reportlab.lib.pagesizes import LETTER, HALF_LETTER, inch, portrait, landscape

__all__ = [
    "THIRD_LETTER",
    "FRANKLIN_CLASSIC",
    "FRANKLIN_COMPACT",
    "AVERY_5160",
    "complete_page_spec",
]

THIRD_LETTER = (4.25 * inch, 6.75 * inch)

FRANKLIN_CLASSIC = {
    "physical_page_size": landscape(LETTER),
    "logical_page_size": HALF_LETTER,
    "logical_page_count": 2,
    "column_count": 1,
    "column_gutter": 0,
    "row_count": 1,
    "binding_margin": 0.25 * inch,
    "left_margin": 0.25 * inch,
    "right_margin": 0.25 * inch,
    "top_margin": 0.25 * inch,
    "bottom_margin": 0.25 * inch,
    "horizontal_padding": 0,
}

FRANKLIN_COMPACT = {
    "physical_page_size": portrait(LETTER),
    "logical_page_size": THIRD_LETTER,
    "logical_page_count": 2,
    "column_count": 1,
    "column_gutter": 0,
    "row_count": 1,
    "binding_margin": 0.25 * inch,
    "left_margin": 0.25 * inch,
    "right_margin": 0.25 * inch,
    "top_margin": 0.25 * inch,
    "bottom_margin": 0.25 * inch,
    "horizontal_padding": 0,
}

# 30-up labels (2 5/8" x  1" each) 3 columns x 10 rows
AVERY_5160 = {
    "physical_page_size": portrait(LETTER),
    "logical_page_size": portrait(LETTER),
    "logical_page_count": 1,
    "column_count": 3,
    "column_gutter": 0,
    "row_count": 10,
    "binding_margin": 0,
    "left_margin": 0.3125 * inch,
    "right_margin": 0.3125 * inch,
    "top_margin": 0.5 * inch,
    "bottom_margin": 0.5 * inch,
    "horizontal_padding": 2,
}


def complete_page_spec(page_spec):
    """
    Ensures that the given page specification dictionary has all of the necessary fields.
    """
    ensure_spec(page_spec, "physical_page_size", LETTER)
    ensure_spec(page_spec, "logical_page_size", page_spec["physical_page_size"])
    ensure_spec(page_spec, "logical_page_count", 1)
    ensure_spec(page_spec, "column_count", 1)
    ensure_spec(page_spec, "row_count", 1)
    ensure_spec(page_spec, "column_gutter", 0)
    ensure_spec(page_spec, "horizontal_padding", 0)
    ensure_spec(page_spec, "binding_margin", 0)
    ensure_spec(page_spec, "left_margin", 0)
    ensure_spec(page_spec, "right_margin", 0)
    ensure_spec(page_spec, "top_margin", 0)
    ensure_spec(page_spec, "bottom_margin", 0)


def ensure_spec(page_spec, spec_name, value):
    if spec_name not in page_spec:
        page_spec[spec_name] = value
