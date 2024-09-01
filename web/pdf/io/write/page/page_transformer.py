import logging
from typing import Optional

from web.pdf.io.read.types import AnyPDFType, Dictionary, Name
from web.pdf.io.write.font.subsetter import Subsetter
from web.pdf.io.write.object.dictionary_transformer import (
    DictionaryTransformer,
)
from web.pdf.io.write.transformer import WriteTransformerState
from web.pdf.pdf import Page
from web.pdf.pdf.document.document import Document

logger = logging.getLogger(__name__)


class PageTransformer(DictionaryTransformer):
    """This implementation of WriteBaseTransformer is responsible for writing
    Dictionary objects of /Type /Page."""

    #
    # CONSTRUCTOR
    #

    #
    # PRIVATE
    #

    #
    # PUBLIC
    #

    def can_be_transformed(self, any_: AnyPDFType):
        """This function returns True if the object to be converted represents an /Page
        Dictionary."""

        return (
            isinstance(any_, Dictionary) and "Type" in any_ and any_["Type"] == "Page"
        )

    def transform(
        self,
        object_to_transform: AnyPDFType,
        context: Optional[WriteTransformerState] = None,
    ):
        """This method writes a /Page Dictionary to a byte stream."""

        assert isinstance(object_to_transform, Dictionary)
        assert isinstance(object_to_transform, Page)
        assert context is not None
        assert context.root_object is not None
        assert isinstance(context.root_object, Document)

        pages_dict = context.root_object["XRef"]["Trailer"]["Root"]["Pages"]

        # add /Parent reference to /Pages
        object_to_transform[Name("Parent")] = self.get_reference(pages_dict, context)

        # mark some keys as non-referencable
        for k in ["ArtBox", "BleedBox", "CropBox", "MediaBox", "TrimBox"]:
            if k in object_to_transform:
                object_to_transform[k].set_is_inline(True)

        # apply subsetting
        if context.apply_font_subsetting:
            Subsetter.apply(object_to_transform)

        # delegate to super
        super(PageTransformer, self).transform(object_to_transform, context)
