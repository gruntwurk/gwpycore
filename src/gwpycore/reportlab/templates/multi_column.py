import logging
from pathlib import Path
from typing import Union

from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame

from .page_sizes import complete_page_spec

LOG = logging.getLogger("main")

__all__ = [
    "doc_template_for_page_spec",
]


def doc_template_for_page_spec(filename: Union[Path, str], page_spec, outline_frames=False):
    """
    Instantiates a doc template that contains one page template which contains a
    frame for each column, or logical page body, or combination thereof.

    :param filename: The file name for the output.

    :param page_spec: A Dictionary with the (logical) page and column specifications.

    :param outline_frames: Whether or not to draw a border aound each frame (for
    debugging), defaults to False.
    """
    doc = BaseDocTemplate(str(filename))
    complete_page_spec(page_spec)
    doc.pagesize = page_spec["physical_page_size"]
    doc.bottomMargin = page_spec["bottom_margin"]
    doc.topMargin = page_spec["top_margin"]
    doc.leftMargin = page_spec["left_margin"]
    doc.rightMargin = page_spec["right_margin"]
    create_col_frames(doc, page_spec, outline_frames=outline_frames)
    return doc


def create_col_frames(doc_template: BaseDocTemplate, page_spec, outline_frames=False):
    """
    For the given doc template, this establishes a page template containing a
    frame for each column, or logical page body, or combination thereof.

    :param doc_template: The BaseDocTemplate instance to modify.

    :param page_spec: A Dictionary with the (logical) page and column specifications.

    :param outline_frames: Whether or not to draw a border aound each frame (for
    debugging), defaults to False.
    """
    frames = []

    for page_number in range(page_spec["logical_page_count"]):
        logical_page_width = page_spec["logical_page_size"][0]
        logical_page_height = page_spec["logical_page_size"][1]
        page_offset = page_number * logical_page_width
        col_count = page_spec["column_count"]
        col_width = (logical_page_width - (col_count - 1) * page_spec["column_gutter"]
                     - page_spec["binding_margin"] - page_spec["left_margin"] - page_spec["right_margin"]) / col_count
        col_height = logical_page_height - page_spec["top_margin"] - page_spec["bottom_margin"]

        for col_number in range(col_count):
            col_offset = page_spec["left_margin"] + col_number * (col_width + page_spec["column_gutter"])
            f = Frame(id=f'page{str(page_number)}_col{str(col_number)}',
                      x1=page_offset + col_offset,
                      y1=page_spec["bottom_margin"],
                      width=col_width, height=col_height,
                      leftPadding=page_spec["horizontal_padding"],
                      rightPadding=page_spec["horizontal_padding"],
                      topPadding=0, bottomPadding=0,
                      showBoundary=outline_frames)
            frames.append(f)
    doc_template.addPageTemplates(PageTemplate(id="physical_page", frames=frames))

