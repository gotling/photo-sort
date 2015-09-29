__author__ = 'marcus'


class NoFileException(Exception):
    pass


class FolderNotEmptyException(Exception):
    def __init__(self, message):
        self.message = message
        super(Exception, self).__init__(message)
