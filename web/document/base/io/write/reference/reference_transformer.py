from typing import Optional

from web.document.base.io.read.types import AnyPDFType, Reference
from web.document.base.io.write.transformer import Transformer, WriteTransformerState


class ReferenceTransform(Transformer):
    """This implementation of WriteBaseTransformer is responsible for writing
    References."""

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
        """This function returns True if the object to be converted represents a
        Reference."""

        return isinstance(any_, Reference)

    def transform(
        self,
        object_to_transform: AnyPDFType,
        context: Optional[WriteTransformerState] = None,
    ):
        """This method writes a Reference to a byte stream."""

        assert (
            context is not None
        ), "A WriteTransformerState must be defined in order to write Reference objects."
        assert context.destination is not None
        assert isinstance(object_to_transform, Reference)

        assert object_to_transform.object_number is not None
        context.destination.write(
            bytes(
                "%d %d R"
                % (
                    object_to_transform.object_number,
                    object_to_transform.generation_number or 0,
                ),
                "latin1",
            )
        )
