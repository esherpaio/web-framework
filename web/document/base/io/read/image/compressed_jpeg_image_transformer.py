import io
import logging
import typing
from typing import Any, Optional, Union

from PIL import Image as PILImage

from web.document.base.io.filter.stream_decode_util import decode_stream
from web.document.base.io.read.pdf_object import PDFObject
from web.document.base.io.read.transformer import ReadTransformerState, Transformer
from web.document.base.io.read.types import AnyPDFType, Name, Stream
from web.document.base.pdf.canvas.event.event_listener import EventListener

logger = logging.getLogger(__name__)


class CompressedJPEGImageTransformer(Transformer):
    """This implementation of ReadBaseTransformer is responsible for reading a jpeg
    image object."""

    #
    # CONSTRUCTOR
    #

    #
    # PRIVATE
    #

    #
    # PUBLIC
    #

    def can_be_transformed(
        self, object_: Union[io.BufferedIOBase, io.RawIOBase, io.BytesIO, AnyPDFType]
    ) -> bool:
        """This function returns True if the object to be transformed is a JPEG
        object."""

        return (
            isinstance(object_, Stream)
            and object_.get("Type", None) in ["XObject", None]
            and object_.get("Subtype", None) == "Image"
            and "Filter" in object_
            and (
                object_["Filter"] == "DCTDecode"
                or (
                    isinstance(object_["Filter"], list)
                    and len(object_["Filter"]) > 1
                    and object_["Filter"][-1] == "DCTDecode"
                )
            )
        )

    def transform(
        self,
        object_to_transform: Union[io.BufferedIOBase, io.RawIOBase, AnyPDFType],
        parent_object: Any,
        context: Optional[ReadTransformerState] = None,
        event_listeners: typing.List[EventListener] = [],
    ) -> Any:
        """This function reads a JPEG Image from a byte stream."""

        assert isinstance(
            object_to_transform, Stream
        ), "object_to_transform must be of type Stream"

        # modify filter (temporarily)
        filters: typing.List = object_to_transform["Filter"]
        filters.pop(len(filters) - 1)

        # decode stream
        decode_stream(object_to_transform)

        # re-apply filter
        filters.append(Name("DCTDecode"))

        # use PIL to read image bytes
        raw_byte_array = object_to_transform["Bytes"]

        try:
            tmp = PILImage.open(io.BytesIO(raw_byte_array))
            tmp.getpixel((0, 0))
        except:  # noqa: E722
            logger.debug(
                "Unable to read compressed jpeg image. Constructing empty image of same dimensions."
            )
            w = int(object_to_transform["Width"])
            h = int(object_to_transform["Height"])
            tmp = PILImage.new("RGB", (w, h), (128, 128, 128))

        # add base methods
        PDFObject.add_pdf_object_methods(tmp)

        # set parent
        tmp.set_parent(parent_object)

        # return
        return tmp
