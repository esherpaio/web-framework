from web.pdf.pdf.canvas.event.event_listener import Event
from web.pdf.pdf.page.page import Page


class BeginPageEvent(Event):
    """This implementation of Event is triggered right before the Canvas is being
    processed."""

    #
    # CONSTRUCTOR
    #

    def __init__(self, page: Page):
        self._page: Page = page

    #
    # PRIVATE
    #

    #
    # PUBLIC
    #

    def get_page(self) -> Page:
        """This function returns the Page that triggered this BeginPageEvent."""

        return self._page
