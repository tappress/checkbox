from starlette import status


class CheckboxException(Exception):
    CODE = "CHECKBOX_EXCEPTION"
    HTTP_STATUS = status.HTTP_400_BAD_REQUEST

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class TooManyRequests(CheckboxException):
    CODE = "TOO_MANY_REQUESTS"
    HTTP_STATUS = status.HTTP_429_TOO_MANY_REQUESTS


class NotFound(CheckboxException):
    CODE = "NOT_FOUND"
    HTTP_STATUS = status.HTTP_404_NOT_FOUND


class Forbidden(CheckboxException):
    CODE = "FORBIDDEN"
    HTTP_STATUS = status.HTTP_403_FORBIDDEN


class Unauthorized(CheckboxException):
    CODE = "UNAUTHORIZED"
    HTTP_STATUS = status.HTTP_401_UNAUTHORIZED


class ResourceAlreadyExists(CheckboxException):
    CODE = "RESOURCE_ALREADY_EXISTS"
    HTTP_STATUS = status.HTTP_409_CONFLICT


class InvalidOffset(CheckboxException):
    CODE = "INVALID_OFFSET"
    HTTP_STATUS = status.HTTP_400_BAD_REQUEST
