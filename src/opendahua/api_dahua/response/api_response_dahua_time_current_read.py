from dataclasses import dataclass
from datetime import datetime
from typing import Self

from opendahua.api_dahua.response.api_response_dahua import ApiResponseDahua


@dataclass(frozen=True)
class ApiResponseDahuaTimeCurrentRead(ApiResponseDahua):
    # Field constants.
    FIELD_TIME_CURRENT = "result"
    
    _time_current: datetime
    
    @classmethod
    def parse(cls, value: dict) -> Self:
        time_current = value[cls.FIELD_TIME_CURRENT]
        
        return cls(time_current)
    
    
    def get_time_current(self) -> datetime:
        return self._time_current
