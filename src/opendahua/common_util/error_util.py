from typing import Type

from opendahua.common_object.dahua_error import DahuaError


class ErrorUtil:
    # Format constants.
    FORMAT_ERROR_UNEXPECTED_CLASS = "Unexpected class \"{unexpected_class}\"."
    FORMAT_ERROR_UNEXPECTED_NONE_VALUE = "Unexpected None value for \"{expected_class}\"."

    @classmethod
    def create_error_unexpected_class(cls, unexpected_class: Type) -> DahuaError:
        return DahuaError(cls.FORMAT_ERROR_UNEXPECTED_CLASS.format(unexpected_class=unexpected_class.__name__))
    
    @classmethod
    def create_error_unexpected_none_value(cls, expected_class: Type) -> DahuaError:
        return DahuaError(cls.FORMAT_ERROR_UNEXPECTED_NONE_VALUE.format(expected_class=expected_class.__name__))
