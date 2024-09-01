import typing

from web.pdf.io.read.types import Name
from web.pdf.pdf.canvas.font.composite_font.cid_font_type_0 import (
    CIDType0Font,
)
from web.pdf.pdf.canvas.font.font import Font


class CIDType2Font(CIDType0Font):
    """A Type 2 CIDFont contains glyph descriptions based on the TrueType font
    format."""

    #
    # CONSTRUCTOR
    #

    def __init__(self):
        super(CIDType2Font, self).__init__()
        self._cid_to_gid_map_cache: typing.Dict[int, int] = {}

    #
    # PRIVATE
    #

    def __deepcopy__(self, memodict={}):
        f_out: CIDType2Font = super(CIDType2Font, self).__deepcopy__(memodict)
        f_out[Name("Subtype")] = Name("CIDFontType2")
        f_out._width_cache = {k: v for k, v in self._width_cache.items()}
        return f_out

    def _empty_copy(self) -> "Font":
        return CIDType2Font()

    #
    # PUBLIC
    #
