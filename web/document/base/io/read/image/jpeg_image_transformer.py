import io
import logging
import typing
from typing import Any, Optional, Union

from PIL import Image as PILImage

from web.document.base.io.read.transformer import ReadTransformerState, Transformer
from web.document.base.io.read.types import AnyPDFType, PDFObject, Stream
from web.document.base.pdf.canvas.event.event_listener import EventListener

logger = logging.getLogger(__name__)


class JPEGImageTransformer(Transformer):
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
            and object_.get("Subtype", None) in ["Image", None]
            and "Filter" in object_
            and (
                object_["Filter"] == "DCTDecode"
                or (
                    isinstance(object_["Filter"], list)
                    and object_["Filter"][0] == "DCTDecode"
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

        # use PIL to read image bytes

        assert isinstance(
            object_to_transform, Stream
        ), "object_to_transform must be of type Stream"

        # warnings
        if object_to_transform.get("Type", None) is None:
            logger.debug("Image object did not specify /Type /XObject.")
        if object_to_transform.get("Subtype", None) is None:
            logger.debug("Image object did not specify /Subtype /Image.")

        # read a pixel
        try:
            tmp = PILImage.open(io.BytesIO(object_to_transform["Bytes"]))
            tmp.getpixel((0, 0))
        except:  # noqa: E722
            w = int(object_to_transform["Width"])
            h = int(object_to_transform["Height"])
            tmp = PILImage.new("RGB", (w, h), (128, 128, 128))

        # add base methods
        PDFObject.add_pdf_object_methods(tmp)

        # return
        return tmp
