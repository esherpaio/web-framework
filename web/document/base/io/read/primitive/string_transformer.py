import io
import typing
from typing import Any, Optional, Union

from doc.io.read.transformer import ReadTransformerState, Transformer
from doc.io.read.types import AnyPDFType, HexadecimalString, Name, String
from doc.pdf.canvas.event.event_listener import EventListener


class StringTransformer(Transformer):
    """This implementation of ReadBaseTransformer is responsible for reading String
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
        """This function returns True if the object to be converted represents a String
        or Hexadecimal String or a Name."""

        return (
            isinstance(object_, String)
            or isinstance(object_, HexadecimalString)
            or isinstance(object_, Name)
        )

    def transform(
        self,
        object_to_transform: Union[io.BufferedIOBase, io.RawIOBase, AnyPDFType],
        parent_object: Any,
        context: Optional[ReadTransformerState] = None,
        event_listeners: typing.List[EventListener] = [],
    ) -> Any:
        """This function reads a String from a byte stream."""

        # set parent
        assert (
            isinstance(object_to_transform, String)
            or isinstance(object_to_transform, HexadecimalString)
            or isinstance(object_to_transform, Name)
        )
        object_to_transform.set_parent(parent_object)
        return object_to_transform
