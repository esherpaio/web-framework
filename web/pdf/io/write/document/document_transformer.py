import logging
import random
import typing
from typing import Any, Optional

from web.pdf.io.read.types import (
    AnyPDFType,
    Dictionary,
    HexadecimalString,
    List,
    Name,
)
from web.pdf.io.write.transformer import Transformer, WriteTransformerState
from web.pdf.pdf.document.document import Document

logger = logging.getLogger(__name__)


class DocumentTransformer(Transformer):
    """This implementation of WriteBaseTransformer is responsible for writing Document
    objects."""

    #
    # CONSTRUCTOR
    #

    #
    # PRIVATE
    #

    @staticmethod
    def _build_empty_document_info_dictionary(object_to_transform: Dictionary) -> None:
        # create Info dictionary if needed
        trailer: typing.Any = object_to_transform["XRef"]["Trailer"]
        assert isinstance(trailer, Dictionary)
        if "Info" not in trailer:
            trailer[Name("Info")] = Dictionary()
        trailer["Info"].set_parent(trailer)

    @staticmethod
    def _invalidate_all_references(object_: AnyPDFType) -> None:
        objects_done: typing.List[AnyPDFType] = []
        objects_todo: typing.List[AnyPDFType] = [object_]
        while len(objects_todo) > 0:
            obj = objects_todo.pop(0)
            if obj in objects_done:
                continue
            objects_done.append(obj)
            try:
                obj.set_reference(None)
            except Exception as ex:
                logger.debug(str(ex))
                pass
            if isinstance(obj, List):
                assert isinstance(obj, List), (
                    "unexpected error while performing _invalidate_all_references"
                )

                for v in obj:
                    objects_todo.append(v)
                continue
            if isinstance(obj, Dictionary):
                assert isinstance(obj, Dictionary), (
                    "unexpected error while performing _invalidate_all_references"
                )

                for k, v in obj.items():
                    objects_todo.append(k)
                    objects_todo.append(v)
                continue

    #
    # PUBLIC
    #

    def can_be_transformed(self, any_: AnyPDFType):
        """This function returns True if the object to be transformed is a Document."""

        return isinstance(any_, Document)

    def transform(
        self, object_to_transform: Any, context: Optional[WriteTransformerState] = None
    ):
        """This method writes a Document object to a byte stream."""

        # write header
        assert context is not None, (
            "A WriteTransformerState must be defined in order to write Document objects."
        )
        assert context.destination is not None, (
            "A WriteTransformerState must be defined in order to write Document objects."
        )

        context.destination.write(b"%PDF-1.7\n")
        context.destination.write(b"%")
        context.destination.write(bytes([226, 227, 207, 211]))
        context.destination.write(b"\n")

        # invalidate all references
        DocumentTransformer._invalidate_all_references(object_to_transform)

        # set /ID
        random_id = HexadecimalString("%032x" % random.randrange(16**32))
        if "ID" not in object_to_transform["XRef"]["Trailer"]:
            object_to_transform["XRef"]["Trailer"][Name("ID")] = List()
            object_to_transform["XRef"]["Trailer"][Name("ID")].set_is_inline(True)
            object_to_transform["XRef"]["Trailer"]["ID"].append(random_id)
            object_to_transform["XRef"]["Trailer"]["ID"].append(random_id)

        else:
            object_to_transform["XRef"]["Trailer"]["ID"][1] = random_id
            object_to_transform["XRef"]["Trailer"]["ID"].set_is_inline(True)

        # /Info
        self._build_empty_document_info_dictionary(object_to_transform)

        # transform XREF
        self.get_root_transformer().transform(object_to_transform["XRef"], context)
