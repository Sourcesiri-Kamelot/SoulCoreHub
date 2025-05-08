class FireworksError(Exception):
    pass


class PermissionError(FireworksError):
    """A permission denied error."""

    pass


class InvalidRequestError(FireworksError):
    """A invalid request error."""

    pass


class APITimeoutError(FireworksError):
    """An API timeout error."""

    pass


class AuthenticationError(FireworksError):
    """A authentication error."""

    pass


class RateLimitError(FireworksError):
    """A rate limit error."""

    pass


class InternalServerError(FireworksError):
    """An internal server error."""

    pass


class ServiceUnavailableError(FireworksError):
    """A service unavailable error."""

    pass


class BadGatewayError(FireworksError):
    """A bad gateway error."""

    pass
