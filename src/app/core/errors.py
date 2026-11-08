class AppError(Exception):
    """Base class for expected business errors (mapped to HTTP responses in one place)."""


class NotFoundError(AppError):
    pass


class ConflictError(AppError):
    pass
