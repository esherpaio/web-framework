import typing
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from web.pdf.pdf import Page

from web.pdf.io.read.types import Dictionary
from web.pdf.pdf.page.page_size import PageSize


class PageInfo(Dictionary):
    """This class represents the meta-information belonging to a single page in a PDF
    document."""

    #
    # CONSTRUCTOR
    #

    def __init__(self, page: "Page"):
        super(PageInfo, self).__init__()
        self._page = page

    #
    # PRIVATE
    #

    #
    # PUBLIC
    #

    def get_height(self) -> Optional[Decimal]:
        """Return the height of the MediaBox.

        This is a rectangle (see 7.9.5, "Rectangles"), expressed in default user space
        units, that shall define the boundaries of the physical medium on which the
        page shall be displayed or printed (see 14.11.2, "Page Boundaries").
        """

        return self._page["MediaBox"][3]

    def get_page_number(self) -> Optional[Decimal]:
        """This function returns the page number."""

        obj = self._page.get_parent().get_parent()  # type: ignore[union-attr]
        if obj is None:
            return None

        kids = obj.get("Kids")  # type: ignore[union-attr]
        assert kids is not None
        c: int = int(obj.get("Count"))  # type: ignore[arg-type,union-attr]

        for i in range(0, c):
            if kids[i] == self._page:
                return Decimal(i)
        return None

    def get_size(self) -> Tuple[Decimal, Decimal]:
        """Return the (width, height) of the MediaBox.

        This is a rectangle (see 7.9.5, "Rectangles"), expressed in default user space
        units, that shall define the boundaries of the physical medium on which the
        page shall be displayed or printed (see 14.11.2, "Page Boundaries").
        """

        return self.get_width() or Decimal(0), self.get_height() or Decimal(0)

    def get_size_as_enum(self) -> Optional[PageSize]:
        """Return the size of the MediaBox as a convenient, well-known, well- defined
        property (e.g. A4_PORTRAIT).

        This is a rectangle (see 7.9.5, "Rectangles"), expressed in default user space
        units, that shall define the boundaries of the physical medium on which the
        page shall be displayed or printed (see 14.11.2, "Page Boundaries").
        """

        w: typing.Optional[Decimal] = self.get_width()
        h: typing.Optional[Decimal] = self.get_height()
        if w is None or h is None:
            return None
        assert w is not None
        assert h is not None
        for p in PageSize:
            if abs(w - p.value[1]) <= 1 and abs(h - p.value[1]) <= 1:
                return p
        return None

    def get_width(self) -> Optional[Decimal]:
        """Return the width of the MediaBox.

        This is a rectangle (see 7.9.5, "Rectangles"), expressed in default user space
        units, that shall define the boundaries of the physical medium on which the
        page shall be displayed or printed (see 14.11.2, "Page Boundaries").
        """

        return self._page["MediaBox"][2]

    def uses_color_images(self) -> Optional[bool]:
        """The PDF operators used in content streams are grouped into categories of
        related operators called procedure sets (see Table 314).

        Each procedure set corresponds to a named resource containing the
        implementations of the operators in that procedure set. The ProcSet entry in a
        content stream’s resource dictionary (see 7.8.3, “Resource Dictionaries”) shall
        hold an array consisting of the names of the procedure sets used in that
        content stream. This method returns whether this PDF uses operators from the
        "ImageC" procedure set.
        """

        return "ImageC" in self._page["Resources"]["ProcSet"]

    def uses_grayscale_images(self) -> Optional[bool]:
        """The PDF operators used in content streams are grouped into categories of
        related operators called procedure sets (see Table 314).

        Each procedure set corresponds to a named resource containing the
        implementations of the operators in that procedure set. The ProcSet entry in a
        content stream’s resource dictionary (see 7.8.3, “Resource Dictionaries”) shall
        hold an array consisting of the names of the procedure sets used in that
        content stream. This method returns whether this PDF uses operators from the
        "ImageB" procedure set.
        """

        return "ImageB" in self._page["Resources"]["ProcSet"]

    def uses_indexed_images(self) -> Optional[bool]:
        """The PDF operators used in content streams are grouped into categories of
        related operators called procedure sets (see Table 314).

        Each procedure set corresponds to a named resource containing the
        implementations of the operators in that procedure set. The ProcSet entry in a
        content stream’s resource dictionary (see 7.8.3, “Resource Dictionaries”) shall
        hold an array consisting of the names of the procedure sets used in that
        content stream. This method returns whether this PDF uses operators from the
        "ImageI" procedure set.
        """

        return "ImageI" in self._page["Resources"]["ProcSet"]

    def uses_painting_and_graphics_state(self) -> Optional[bool]:
        """The PDF operators used in content streams are grouped into categories of
        related operators called procedure sets (see Table 314).

        Each procedure set corresponds to a named resource containing the
        implementations of the operators in that procedure set. The ProcSet entry in a
        content stream’s resource dictionary (see 7.8.3, “Resource Dictionaries”) shall
        hold an array consisting of the names of the procedure sets used in that
        content stream. This method returns whether this PDF uses operators from the
        "PDF" procedure set.
        """

        return "PDF" in self._page["Resources"]["ProcSet"]

    def uses_text(self) -> Optional[bool]:
        """The PDF operators used in content streams are grouped into categories of
        related operators called procedure sets (see Table 314).

        Each procedure set corresponds to a named resource containing the
        implementations of the operators in that procedure set. The ProcSet entry in a
        content stream’s resource dictionary (see 7.8.3, “Resource Dictionaries”) shall
        hold an array consisting of the names of the procedure sets used in that
        content stream. This method returns whether this PDF uses operators from the
        "Text" procedure set.
        """

        return "Text" in self._page["Resources"]["ProcSet"]
