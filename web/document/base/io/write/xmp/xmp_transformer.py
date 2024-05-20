import logging
import xml.etree.ElementTree as ET
from typing import Optional

from web.document.base.io.read.types import AnyPDFType, Name, Reference, Stream
from web.document.base.io.read.types import Decimal as bDecimal
from web.document.base.io.write.transformer import Transformer, WriteTransformerState

logger = logging.getLogger(__name__)


class XMPTransformer(Transformer):
    """This implementation of WriteBaseTransformer is responsible for writing XMP meta-
    data information."""

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
        """This function returns True if the object to be converted represents an XML
        element."""

        return isinstance(any_, ET.Element)

    def transform(
        self,
        object_to_transform: AnyPDFType,
        context: Optional[WriteTransformerState] = None,
    ):
        """This method writes an ET.Element (representing XMP meta information) to a
        byte stream."""

        assert isinstance(object_to_transform, ET.Element)

        assert (
            context is not None
        ), "A WriteTransformerState must be defined in order to write XMP objects."
        assert (
            context.destination is not None
        ), "A WriteTransformerState must be defined in order to write XMP objects."

        # build stream
        out_value = Stream()
        out_value[Name("Type")] = Name("Metadata")
        out_value[Name("Subtype")] = Name("XML")

        bts = ET.tostring(object_to_transform)
        out_value[Name("DecodedBytes")] = bts
        out_value[Name("Bytes")] = bts
        out_value[Name("Length")] = bDecimal(len(bts))

        # start object if needed
        started_object = False
        ref = out_value.get_reference()
        if ref is not None:
            assert isinstance(ref, Reference)
            if ref.object_number is not None and ref.byte_offset is None:
                started_object = True
                self._start_object(out_value, context)

        # pass stream along to other transformer
        self.get_root_transformer().transform(out_value, context)

        # end object if needed
        if started_object:
            self._end_object(context)
