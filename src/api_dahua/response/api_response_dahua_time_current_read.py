from dataclasses import dataclass
from datetime import datetime
from typing import Self

from src.api_dahua.response.api_response_dahua import ApiResponseDahua


@dataclass(frozen=True)
class ApiResponseDahuaTimeCurrentRead(ApiResponseDahua):
    _time_current: datetime
    
    FIELD_TIME_CURRENT = "result"
    
    
    @classmethod
    def parse(cls, value: dict) -> Self:
        time_current = datetime.fromisoformat(value[cls.FIELD_TIME_CURRENT])
        
        return cls(time_current)
    
    
    def get_time_current(self) -> datetime:
        return self._time_current
    