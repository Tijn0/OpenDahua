

class Logger:
    # Format constants.
    PREFIX_MESSAGE_DEBUG = 'debug'
    PREFIX_MESSAGE_INFO = 'info'
    PREFIX_MESSAGE_WARNING = 'warning'
    PREFIX_MESSAGE_ERROR = 'error'

    # Format constants.
    FORMAT_MESSAGE = '[{prefix}] - {message}'

    def __init__(self):
        pass
    
    @classmethod
    def info(cls, message: str|bytes) -> None:
        print(cls.FORMAT_MESSAGE.format(prefix=cls.PREFIX_MESSAGE_INFO, message=message))

    @classmethod
    def debug(cls, message: str|bytes) -> None:
        print(cls.FORMAT_MESSAGE.format(prefix=cls.PREFIX_MESSAGE_DEBUG, message=message))
    
    @classmethod
    def warning(cls, message: str|bytes):
        print(cls.FORMAT_MESSAGE.format(prefix=cls.PREFIX_MESSAGE_WARNING, message=message))
