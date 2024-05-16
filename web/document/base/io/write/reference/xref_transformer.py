import typing
from typing import Optional

from doc.io.read.types import AnyPDFType, Decimal, Dictionary, Name, Reference
from doc.io.write.transformer import Transformer, WriteTransformerState
from doc.pdf.xref.xref import XREF


class XREFTransformer(Transformer):
    """This implementation of WriteBaseTransformer is responsible for writing XREF
    objects."""

    #
    # CONSTRUCTOR
    #

    #
    # PRIVATE
    #

    @staticmethod
    def _section_xref(context: Optional[WriteTransformerState] = None):
        assert (
            context is not None
        ), "A WriteTransformerState must be defined in order to write XREF objects."

        # get all references
        indirect_objects: typing.List[AnyPDFType] = [
            item
            for sublist in [v for k, v in context.indirect_objects_by_hash.items()]
            for item in sublist
        ]
        references: typing.List[Reference] = []
        for obj in indirect_objects:
            ref = obj.get_reference()
            if ref is not None:
                references.append(ref)
        # sort
        references.sort(key=lambda x: (x.object_number or 0))

        # insert magic entry if needed
        if len(references) == 0 or references[0].generation_number != 65535:
            references.insert(
                0,
                Reference(
                    generation_number=65535,
                    object_number=0,
                    byte_offset=0,
                    is_in_use=False,
                ),
            )

        # divide into sections
        sections = [[references[0]]]
        for i in range(1, len(references)):
            ref = references[i]
            prev_object_number = sections[-1][-1].object_number
            assert prev_object_number is not None
            if ref.object_number == prev_object_number + 1:
                sections[-1].append(ref)
            else:
                sections.append([ref])

        # return
        return sections

    #
    # PUBLIC
    #

    def can_be_transformed(self, any_: AnyPDFType):
        """This function returns True if the object to be converted represents a cross-
        reference table."""

        return isinstance(any_, XREF)

    def transform(
        self,
        object_to_transform: AnyPDFType,
        context: Optional[WriteTransformerState] = None,
    ):
        """This method writes an XREF to a byte stream."""

        assert isinstance(object_to_transform, XREF)
        assert "Trailer" in object_to_transform
        assert isinstance(object_to_transform["Trailer"], Dictionary)

        assert (
            context is not None
        ), "A WriteTransformerState must be defined in order to write XREF objects."
        assert (
            context.destination is not None
        ), "A WriteTransformerState must be defined in order to write XREF objects."

        trailer_out = Dictionary()

        # /Root

        trailer_out[Name("Root")] = self.get_reference(
            object_to_transform["Trailer"]["Root"], context
        )

        # /Info

        if "Info" in object_to_transform["Trailer"]:
            trailer_out[Name("Info")] = self.get_reference(
                object_to_transform["Trailer"]["Info"], context
            )

        # /Size

        if (
            "Trailer" in object_to_transform
            and "Size" in object_to_transform["Trailer"]
        ):
            trailer_out[Name("Size")] = object_to_transform["Trailer"]["Size"]
        else:
            trailer_out[Name("Size")] = Decimal(
                0
            )  # we'll recalculate this later anyway

        # /ID
        if "ID" in object_to_transform["Trailer"]:
            trailer_out[Name("ID")] = object_to_transform["Trailer"]["ID"]

        # write /Info object

        if "Info" in object_to_transform["Trailer"]:
            self.get_root_transformer().transform(
                object_to_transform["Trailer"]["Info"], context
            )

        # write /Root object
        self.get_root_transformer().transform(
            object_to_transform["Trailer"]["Root"], context
        )

        # write /XREF
        start_of_xref = context.destination.tell()
        context.destination.write(bytes("xref\n", "latin1"))
        for section in self._section_xref(context):
            context.destination.write(
                bytes("%d %d\n" % (section[0].object_number, len(section)), "latin1")
            )
            for r in section:
                if r.is_in_use:
                    context.destination.write(
                        bytes("{0:010d} 00000 n\r\n".format(r.byte_offset), "latin1")
                    )
                else:
                    context.destination.write(
                        bytes("{0:010d} 00000 f\r\n".format(r.byte_offset), "latin1")
                    )

        # update /Size
        trailer_out[Name("Size")] = Decimal(
            sum([len(v) for k, v in context.indirect_objects_by_hash.items()]) + 1
        )

        # write /Trailer
        context.destination.write(bytes("trailer\n", "latin1"))
        self.get_root_transformer().transform(trailer_out, context)
        context.destination.write(bytes("startxref\n", "latin1"))

        # write byte offset of last cross-reference section
        context.destination.write(bytes(str(start_of_xref) + "\n", "latin1"))

        # write EOF
        context.destination.write(bytes("%%EOF", "latin1"))
