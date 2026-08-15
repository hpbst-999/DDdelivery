class DomainException(Exception):
    pass

class InvalidPhoneNumberError(DomainException):
    pass
class OTPVerificationFailedError(DomainException):
    pass
class InvalidEmailError(DomainException):
    pass
class InvalidCoordinatesError(DomainException):
    pass
class AccountNotFoundError(DomainException): 
    pass
class ProfileNotFoundError(DomainException): 
    pass
class SessionNotFoundError(DomainException):
    pass


class OTPExpiredError(DomainException):
    pass

class OTPMaxAttemptsExceededError(DomainException):
    pass

class OTPRateLimitError(DomainException):
    pass

class InvalidOTPCodeError(DomainException):
    pass