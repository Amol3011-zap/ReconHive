class ReconHiveException(Exception):
    pass

class NotFoundError(ReconHiveException):
    pass

class ValidationError(ReconHiveException):
    pass

class UnauthorizedError(ReconHiveException):
    pass

class ForbiddenError(ReconHiveException):
    pass

class ConflictError(ReconHiveException):
    pass

class DatabaseError(ReconHiveException):
    pass
