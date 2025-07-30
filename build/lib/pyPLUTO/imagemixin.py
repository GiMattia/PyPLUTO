from .imagestate import ImageState


class ImageMixin:
    """Mixin class for image handling. It provides properties and methods
    related to the image state and axes."""

    state: ImageState

    @property
    def ax(self):
        """Returns the axes of the image."""
        return self.state.ax
