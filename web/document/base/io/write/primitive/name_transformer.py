from typing import Optional

from doc.io.read.types import AnyPDFType, Name
from doc.io.write.transformer import Transformer, WriteTransformerState


class NameTransformer(Transformer):
    """This implementation of WriteBaseTransformer is responsible for writing Name
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

    def can_be_transformed(self, any_: AnyPDFType):
        """This function returns True if the object to be converted represents a Name
        object."""

        return isinstance(any_, Name)

    def transform(
        self,
        object_to_transform: AnyPDFType,
        context: Optional[WriteTransformerState] = None,
    ):
        """This method writes a Name to a byte stream."""

        assert context is not None
        assert context.destination is not None
        assert isinstance(object_to_transform, Name)

        context.destination.write(bytes("/" + str(object_to_transform), "latin1"))
