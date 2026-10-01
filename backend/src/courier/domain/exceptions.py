class DomainException(Exception):
    pass


class InvalidEmailError(DomainException):
    pass


class InvalidPhoneNumberError(DomainException):
    pass


class ProfileNotFoundError(DomainException):
    pass


class CourierNotVerifiedError(DomainException):
    pass


class InvalidCourierStatusTransitionError(DomainException):
    pass
