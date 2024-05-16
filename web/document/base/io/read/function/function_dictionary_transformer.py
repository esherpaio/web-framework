import io
import typing
from decimal import Decimal
from typing import Any, Optional, Union

from web.document.base.io.filter.stream_decode_util import decode_stream
from web.document.base.io.read.transformer import ReadTransformerState, Transformer
from web.document.base.io.read.types import (
    AnyPDFType,
    Dictionary,
    Function,
    Name,
    Reference,
    Stream,
)
from web.document.base.pdf.canvas.event.event_listener import EventListener


class FunctionDictionaryTransformer(Transformer):
    """This implementation of ReadBaseTransformer is responsible for reading a Function
    Dictionary."""

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
        """This function returns True if the object to be transformed is a Dictionary
        with /FunctionType key."""

        return (
            isinstance(object_, dict)
            and "FunctionType" in object_
            and isinstance(object_["FunctionType"], Decimal)
            and int(object_["FunctionType"]) in [0, 2, 3, 4]
        )

    def transform(
        self,
        object_to_transform: Union[io.BufferedIOBase, io.RawIOBase, AnyPDFType],
        parent_object: Any,
        context: Optional[ReadTransformerState] = None,
        event_listeners: typing.List[EventListener] = [],
    ) -> Any:
        """This function reads a Dictionary with /FunctionType key from a byte
        stream."""

        assert isinstance(
            object_to_transform, Dictionary
        ), "object_to_transform must be of type Dictionary."
        assert (
            "FunctionType" in object_to_transform
        ), "object_to_transform Dictionary must be FunctionType."
        assert isinstance(
            object_to_transform["FunctionType"], Decimal
        ), "object_to_transform must contain a valid /FunctionType entry."

        function_type: int = int(object_to_transform["FunctionType"])
        assert function_type in [0, 2, 3, 4], "FunctionType must be in [0, 2, 3, 4]"

        transformed_object: Function = Function()

        if isinstance(object_to_transform, Stream):
            decode_stream(object_to_transform)
            transformed_object[Name("Bytes")] = object_to_transform["Bytes"]
            transformed_object[Name("DecodedBytes")] = object_to_transform[
                "DecodedBytes"
            ]

        # resolve references in stream dictionary

        assert context is not None, "context must be defined to read Dictionary objects"
        assert (
            context.tokenizer is not None
        ), "context.tokenizer must be defined to read Dictionary objects"

        xref = parent_object.get_root().get("XRef")
        for k, v in object_to_transform.items():
            if isinstance(v, Reference):
                v = xref.get_object(v, context.source, context.tokenizer)
                transformed_object[k] = v

        # convert (remainder of) stream dictionary
        for k, v in object_to_transform.items():
            if not isinstance(v, Reference):
                v = self.get_root_transformer().transform(
                    v, transformed_object, context, []
                )
                if v is not None:
                    transformed_object[k] = v

        # linkage
        transformed_object.set_parent(parent_object)

        # return
        return transformed_object
