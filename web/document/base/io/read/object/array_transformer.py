import io
import typing
from typing import Any, Optional, Union

from web.document.base.io.read.transformer import ReadTransformerState, Transformer
from web.document.base.io.read.types import AnyPDFType, List
from web.document.base.pdf.canvas.event.event_listener import EventListener


class ArrayTransformer(Transformer):
    """This implementation of BaseTransformer converts a PDFArray to a List."""

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
        """This function returns True if the object to be transformed is a List."""

        return isinstance(object_, List)

    def transform(
        self,
        object_to_transform: Union[io.BufferedIOBase, io.RawIOBase, AnyPDFType],
        parent_object: Any,
        context: Optional[ReadTransformerState] = None,
        event_listeners: typing.List[EventListener] = [],
    ) -> Any:
        """This function reads a List from a byte stream."""

        # create root object
        assert isinstance(
            object_to_transform, List
        ), "object_to_transform must be of type List"
        object_to_transform.set_parent(parent_object)

        # transform child(ren)
        for i in range(0, len(object_to_transform)):
            object_to_transform[i] = self.get_root_transformer().transform(
                object_to_transform[i], object_to_transform, context, event_listeners
            )

        # return
        return object_to_transform
