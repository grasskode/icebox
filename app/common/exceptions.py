class IceboxError(Exception):
    def __init__(self, message):
        self.message = message

class IceboxStorageError(Exception):
    pass
