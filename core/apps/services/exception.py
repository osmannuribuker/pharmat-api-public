from rest_framework.exceptions import PermissionDenied
from rest_framework import status


class PermissionException(PermissionDenied):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Bu işlemi gerçekleştirmek için yetkiniz yok"

    def __init__(self, detail=None):
        if detail is not None:
            self.detail = detail

class AcceptableException(PermissionDenied):
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    default_detail = "Girdiğiniz değerler gerçeli değil"

    def __init__(self, detail=None):
        if detail is not None:
            self.detail = detail   