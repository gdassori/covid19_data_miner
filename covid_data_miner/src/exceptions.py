class Covid19Exception(Exception):
    pass


class InvalidPath(Covid19Exception):
    pass


class InvalidConfigFileName(Covid19Exception):
    pass


class DirectoryNotExists(Covid19Exception):
    pass


class SourceDuplicatedException(Covid19Exception):
    pass


class UnknownSourceException(Covid19Exception):
    pass


class UnknownTagForSourceException(Covid19Exception):
    pass


class ErrorSavingConfigFile(Covid19Exception):
    pass


class NoPointsForSource(Covid19Exception):
    pass


class ProjectionRewindFailed(Covid19Exception):
    pass
