from rest_framework.exceptions import APIException

class ItemNotFound(APIException):
    status_code = 404
    default_detail = 'Item Not found'
    default_code = 'Incorrect data'


class InvalidActivationCode(APIException):
    status_code = 404
    default_detail = 'Activation link is invalid'
    default_code = 'Incorrect data'