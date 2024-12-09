from rest_framework import status
from rest_framework.exceptions import APIException

class NotAllowedError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You are not allowed to perform this operation."
    default_code = None

class ExistsError(APIException):
    status_code     = status.HTTP_409_CONFLICT
    default_detail  = "This data already exists."
    default_code    = None

class NotExistsError(APIException):
    status_code     = status.HTTP_404_NOT_FOUND
    default_detail  = "This data does not exist."
    default_code    = None

class UnauthorizedError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "You are not allowed to perform this operation."
    default_code = None

class BadInputError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Something is wrong with your input"
    default_code = None

class SectionEndError(APIException):
    status_code = status.HTTP_408_REQUEST_TIMEOUT
    default_detail = "Your Section had expired"
    default_code = None


class ValidationException(Exception):
    pass