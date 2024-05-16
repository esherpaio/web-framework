import io
import typing

import PIL

from web.document.base.io.read.types import AnyPDFType, Dictionary, Name, Stream
from web.document.base.pdf.canvas.event.image_render_event import ImageRenderEvent
from web.document.base.pdf.canvas.operator.canvas_operator import CanvasOperator


class Do(CanvasOperator):
    """Paint the specified XObject. The operand name shall appear as a key in the
    XObject subdictionary of the current resource dictionary (see 7.8.3, "Resource
    Dictionaries"). The associated value shall be a stream whose Type entry, if
    present, is XObject.

    The effect of Do depends on the value of the XObject’s Subtype entry, which may be
    Image (see 8.9.5, "Image Dictionaries"), Form (see 8.10, "Form XObjects"), or PS
    (see 8.8.2, "PostScript XObjects").
    """

    def __init__(self):
        super().__init__("Do", 1)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invoke the Do operator."""

        # get Page
        canvas = canvas_stream_processor.get_canvas()
        canvas_stream_processor.get_page()

        # get XObject
        assert isinstance(operands[0], Name)
        xobject = canvas_stream_processor.get_resource("XObject", str(operands[0]))

        # render Image objects
        if isinstance(xobject, PIL.Image.Image):
            for line in event_listeners:
                line._event_occurred(
                    ImageRenderEvent(
                        graphics_state=canvas.graphics_state, image=xobject
                    )
                )
            return

        # Form XObject
        if (
            isinstance(xobject, Stream)
            and "Subtype" in xobject
            and xobject["Subtype"] == "Form"
        ):
            # execute XObject
            xobject_resources: Dictionary = (
                xobject["Resources"] if "Resources" in xobject else {}
            )
            child_canvas_stream_processor = (
                canvas_stream_processor.create_child_canvas_stream_processor(
                    [xobject_resources]
                )
            )
            child_canvas_stream_processor.read(
                io.BytesIO(xobject["DecodedBytes"]), event_listeners
            )

            # return
            return

        pass
