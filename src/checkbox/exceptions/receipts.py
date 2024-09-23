from starlette import status

from checkbox.exceptions.base import CheckboxException


class PaymentAmountMismatch(CheckboxException):
    CODE = "PAYMENT_AMOUNT_MISMATCH"
    HTTP_STATUS = status.HTTP_400_BAD_REQUEST
