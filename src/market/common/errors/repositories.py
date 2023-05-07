class RepositoryError(Exception):
    pass


class NotFoundError(RepositoryError):
    pass


class AlreadyExistsError(RepositoryError):
    pass
