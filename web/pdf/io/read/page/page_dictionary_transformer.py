import io
import typing
import zlib
from typing import Any, Dict, Optional, Union

from web.pdf.io.read.transformer import ReadTransformerState, Transformer
from web.pdf.io.read.types import AnyPDFType, Dictionary, List, Name, Stream
from web.pdf.io.read.types import Decimal as bDecimal
from web.pdf.pdf.canvas.canvas import Canvas
from web.pdf.pdf.canvas.canvas_stream_processor import CanvasStreamProcessor
from web.pdf.pdf.canvas.event.begin_page_event import BeginPageEvent
from web.pdf.pdf.canvas.event.end_page_event import EndPageEvent
from web.pdf.pdf.canvas.event.event_listener import EventListener
from web.pdf.pdf.page.page import Page


class PageDictionaryTransformer(Transformer):
    """This implementation of ReadBaseTransformer is responsible for reading Page
    objects."""

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
        """This function returns True if the object to be converted represents a /Page
        Dictionary."""

        return (
            isinstance(object_, Dict)
            and "Type" in object_
            and object_["Type"] == "Page"
        )

    def transform(
        self,
        object_to_transform: Union[io.BufferedIOBase, io.RawIOBase, AnyPDFType],
        parent_object: Any,
        context: Optional[ReadTransformerState] = None,
        event_listeners: typing.List[EventListener] = [],
    ) -> Any:
        """This function reads a /Page Dictionary from a byte stream."""

        if isinstance(object_to_transform, Page):
            return object_to_transform

        # convert dictionary like structure
        page_out = Page()
        page_out.set_parent(parent_object)

        # convert key/value pairs

        assert isinstance(object_to_transform, Dictionary), (
            "object_to_transform must be of type Dictionary"
        )

        for k, v in object_to_transform.items():
            # avoid circular reference
            if k == "Parent":
                continue
            v = self.get_root_transformer().transform(
                v, page_out, context, event_listeners
            )
            if v is not None:
                page_out[k] = v

        # send out BeginPageEvent
        for listener in event_listeners:
            listener._event_occurred(BeginPageEvent(page_out))

        # check whether `Contents` exists
        if "Contents" not in page_out:
            return
        if not isinstance(page_out["Contents"], List) and not isinstance(
            page_out["Contents"], Stream
        ):
            return

        # Force content to be Stream (rather than List)
        contents = page_out["Contents"]
        if isinstance(contents, List):
            bts = b"".join([x["DecodedBytes"] + b" " for x in contents])
            page_out[Name("Contents")] = Stream()
            assert isinstance(page_out["Contents"], Stream)
            page_out["Contents"][Name("DecodedBytes")] = bts
            page_out["Contents"][Name("Bytes")] = zlib.compress(bts, 9)
            page_out["Contents"][Name("Filter")] = Name("FlateDecode")
            page_out["Contents"][Name("Length")] = bDecimal(len(bts))
            contents = page_out["Contents"]
            contents.set_parent(page_out)

        # create Canvas
        canvas: Canvas = Canvas().set_parent(page_out)

        # If there are no event listeners, processing the page has no effect we may as
        # well skip it (because it is very labour-intensive).
        if len(event_listeners) > 0:
            # create CanvasStreamProcessor
            CanvasStreamProcessor(page_out, canvas, []).read(
                io.BytesIO(contents["DecodedBytes"]), event_listeners
            )

        # send out EndPageEvent
        for listener in event_listeners:
            listener._event_occurred(EndPageEvent(page_out))

        # return
        return page_out
