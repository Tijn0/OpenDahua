from dataclasses import dataclass

from src.api.api_response import ApiResponse
from src.api_dahua.response.api_response_dahua import ApiResponseDahua


@dataclass(frozen=True)
class ApiResponseDahuaMachineNameRead(ApiResponseDahua):
    # Field constants.
    FIELD_NAME = "name"
    
    _name: str
    
    @classmethod
    def parse(cls, value: dict) -> ApiResponse:
        name = value[cls.FIELD_NAME]
        
        return cls(name)
        

    def get_name_string(self) -> str:
        return self._name
