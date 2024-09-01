import logging
import typing
from typing import Optional

from web.pdf.io.read.types import AnyPDFType, Dictionary, Name
from web.pdf.io.write.object.dictionary_transformer import (
    DictionaryTransformer,
)
from web.pdf.io.write.transformer import WriteTransformerState

logger = logging.getLogger(__name__)


class PagesTransformer(DictionaryTransformer):
    """This implementation of WriteBaseTransformer is responsible for writing
    Dictionary objects of /Type /Pages."""

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
        """This function returns True if the object to be converted represents a /Pages
        Dictionary."""

        return (
            isinstance(any_, Dictionary) and "Type" in any_ and any_["Type"] == "Pages"
        )

    def transform(
        self,
        object_to_transform: AnyPDFType,
        context: Optional[WriteTransformerState] = None,
    ):
        """This method writes a /Pages Dictionary to a byte stream."""

        assert isinstance(object_to_transform, Dictionary)
        assert context is not None

        # /Kids can be written immediately
        object_to_transform[Name("Kids")].set_is_inline(True)

        # queue writing of /Page objects
        queue: typing.List[AnyPDFType] = []
        for i, k in enumerate(object_to_transform["Kids"]):
            queue.append(k)
            object_to_transform["Kids"][i] = self.get_reference(k, context)

        # delegate to super
        super(PagesTransformer, self).transform(object_to_transform, context)

        # write /Page objects
        for p in queue:
            self.get_root_transformer().transform(p, context)

        # restore /Kids
        for i, k in enumerate(queue):
            object_to_transform["Kids"][i] = k
