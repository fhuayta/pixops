class PixOpsError(Exception):
    """Base error for the package."""


class UnsupportedInputError(PixOpsError):
    """Path or input type cannot be processed."""


class OutputError(PixOpsError):
    """Output path is missing or invalid."""


class TransformError(PixOpsError):
    """A resize, canvas, or encode step is invalid."""
