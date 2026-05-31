from datetime import datetime
import os
from typing import Any

from opendahua.object.log_level import LogLevel


class Logger:
    # Error constants.
    ERROR_UNEXPECTED_LOG_LEVEL = "Unexpected log level \"{log_level}\"."
    
    # Format constants.
    FORMAT_MESSAGE = "{timestamp} [{log_level}] - {message}"
    FORMAT_TIMESTAMP = "%Y-%m-%d %H:%M:%S.%f"
    
    # Log level.
    LOG_LEVEL = LogLevel(os.getenv("LOG_LEVEL"))
    
    
    @classmethod
    def debug(cls, message: Any) -> None:
        cls._log(LogLevel.DEBUG, message)
        
        
    @classmethod
    def info(cls, message: Any) -> None:
        cls._log(LogLevel.INFO, message)
    
    
    @classmethod
    def warning(cls, message: Any) -> None:
        cls._log(LogLevel.WARNING, message)
    
    
    @classmethod
    def error(cls, message: Any) -> None:
        cls._log(LogLevel.ERROR, message)


    @classmethod
    def _log(cls, log_level: LogLevel, message: Any) -> None:
        if cls._should_log(log_level):
            timestamp = cls._generate_timestamp_string()
            
            print(cls.FORMAT_MESSAGE.format(timestamp=timestamp, log_level=log_level.value, message=message))
        else:
            # Don't log.
            pass
    
    
    @classmethod
    def _should_log(cls, log_level: LogLevel) -> bool:
        match log_level:
            case LogLevel.DEBUG:
                return cls.LOG_LEVEL == LogLevel.DEBUG
            case LogLevel.INFO:
                return (cls.LOG_LEVEL == LogLevel.DEBUG or
                        cls.LOG_LEVEL == LogLevel.INFO)
            case LogLevel.WARNING:
                return (cls.LOG_LEVEL == LogLevel.DEBUG or
                        cls.LOG_LEVEL == LogLevel.INFO or
                        cls.LOG_LEVEL == LogLevel.WARNING)
            case LogLevel.ERROR:
                return (cls.LOG_LEVEL == LogLevel.DEBUG or
                        cls.LOG_LEVEL == LogLevel.INFO or
                        cls.LOG_LEVEL == LogLevel.WARNING or
                        cls.LOG_LEVEL == LogLevel.ERROR)
            case _:
                raise Exception(cls.ERROR_UNEXPECTED_LOG_LEVEL.format(log_level=log_level.value))
            
            
    @classmethod
    def _generate_timestamp_string(cls) -> str:
        return datetime.now().strftime(cls.FORMAT_TIMESTAMP)
