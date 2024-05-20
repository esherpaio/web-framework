import io
from typing import Optional, Union

from web.document.base.io.read.types import AnyPDFType
from web.document.base.io.write.document.document_transformer import DocumentTransformer
from web.document.base.io.write.document.information_dictionary_transformer import (
    InformationDictionaryTransformer,
)
from web.document.base.io.write.image.image_transformer import ImageTransformer
from web.document.base.io.write.object.array_transformer import ArrayTransformer
from web.document.base.io.write.object.dictionary_transformer import (
    DictionaryTransformer,
)
from web.document.base.io.write.object.stream_transformer import StreamTransformer
from web.document.base.io.write.page.page_transformer import PageTransformer
from web.document.base.io.write.page.pages_transformer import PagesTransformer
from web.document.base.io.write.primitive.boolean_transformer import BooleanTransformer
from web.document.base.io.write.primitive.name_transformer import NameTransformer
from web.document.base.io.write.primitive.number_transformer import NumberTransformer
from web.document.base.io.write.primitive.string_transformer import StringTransformer
from web.document.base.io.write.reference.reference_transformer import (
    ReferenceTransform,
)
from web.document.base.io.write.reference.xref_transformer import XREFTransformer
from web.document.base.io.write.transformer import Transformer, WriteTransformerState
from web.document.base.io.write.xmp.xmp_transformer import XMPTransformer


class AnyObjectTransformer(Transformer):
    """This implementation of WriteBaseTransformer acts as an aggregator for its child
    transformers, allowing it to transform AnyPDFType."""

    #
    # CONSTRUCTOR
    #

    def __init__(self):
        super().__init__()
        # special object types
        self.add_child_transformer(DocumentTransformer())
        self.add_child_transformer(XREFTransformer())
        self.add_child_transformer(PagesTransformer())
        self.add_child_transformer(PageTransformer())
        self.add_child_transformer(InformationDictionaryTransformer())
        # object types
        self.add_child_transformer(ArrayTransformer())
        self.add_child_transformer(StreamTransformer())
        self.add_child_transformer(DictionaryTransformer())
        self.add_child_transformer(ImageTransformer())
        self.add_child_transformer(XMPTransformer())
        # primitives
        self.add_child_transformer(NameTransformer())
        self.add_child_transformer(StringTransformer())
        self.add_child_transformer(ReferenceTransform())
        self.add_child_transformer(NumberTransformer())
        self.add_child_transformer(BooleanTransformer())

    #
    # PRIVATE
    #

    #
    # PUBLIC
    #

    def can_be_transformed(self, object_to_transform: AnyPDFType):
        """This function returns True if the object to be transformed can be
        transformed by this WriteBaseTransformer."""

        return False

    def transform(
        self,
        object_to_transform: AnyPDFType,
        context: Optional[WriteTransformerState] = None,
        destination: Optional[Union[io.BufferedIOBase, io.RawIOBase]] = None,
    ):
        """This method writes an (PDF) object to a byte stream."""

        if context is None:
            super().transform(
                object_to_transform,
                WriteTransformerState(
                    destination=destination, root_object=object_to_transform
                ),
            )
        else:
            super().transform(object_to_transform, context)
