import io
import logging
import typing
from typing import Any, Optional, Union

from doc.io.read.pdf_object import PDFObject
from doc.io.read.transformer import ReadTransformerState, Transformer
from doc.io.read.types import AnyPDFType, Stream
from doc.pdf.canvas.event.event_listener import EventListener
from PIL import Image

logger = logging.getLogger(__name__)


class JPEG2000ImageTransformer(Transformer):
    """This implementation of ReadBaseTransformer is responsible for reading a jpeg2000
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
        """This function returns True if the object to be transformed is a JPEG2000
        object."""

        return (
            isinstance(object_, dict)
            and object_.get("Type", None) in ["XObject", None]
            and object_.get("Subtype", None) == "Image"
            and "Filter" in object_
            and (
                object_["Filter"] == "JPXDecode"
                or (
                    isinstance(object_["Filter"], list)
                    and object_["Filter"][0] == "JPXDecode"
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
        """This function reads a JPEG2000 Image from byte stream."""

        # use PIL to read image bytes

        assert isinstance(
            object_to_transform, Stream
        ), "object_to_transform must be of type Stream"

        try:
            tmp = Image.open(io.BytesIO(object_to_transform["Bytes"]))
            tmp.getpixel((0, 0))
        except:  # noqa: E722
            logger.debug(
                "Unable to read jpeg2000 image. Constructing empty image of same dimensions."
            )
            w = int(object_to_transform["Width"])
            h = int(object_to_transform["Height"])
            tmp = Image.new("RGB", (w, h), (128, 128, 128))

        # add base methods
        PDFObject.add_pdf_object_methods(tmp)

        # set parent
        tmp.set_parent(parent_object)

        # return
        return tmp
