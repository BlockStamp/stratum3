class ProtocolException(Exception):
    pass


class TransportException(Exception):
    pass


class ServiceException(Exception):
    code = -2


class SignatureException(ServiceException):
    code = -21


class UnknownSignatureAlgorithmException(SignatureException):
    code = -22


class UnknownSignatureIdException(SignatureException):
    code = -22


class SignatureVerificationFailedException(SignatureException):
    code = -23


class MethodNotFoundException(ServiceException):
    code = -3


class ServiceNotFoundException(ServiceException):
    code = -2


class MissingServiceTypeException(ServiceException):
    code = -2


class MissingServiceVendorException(ServiceException):
    code = -2


class MissingServiceIsDefaultException(ServiceException):
    code = -2


class DefaultServiceAlreadyExistException(ServiceException):
    code = -2


class RemoteServiceException(Exception):
    pass
