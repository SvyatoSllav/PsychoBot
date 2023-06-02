from enum import Enum


class PaymentStatus(Enum):

    NONE = "NONE"
    NEW = "NEW"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    CANCELED = "CANCELED"
    REFUNDED = "REFUNDED"

    @classmethod
    def choices(cls):
        # print(tuple((i.name, i.value) for i in cls))
        return tuple((i.name, i.value) for i in cls)


def check_payment_status():
    pass
