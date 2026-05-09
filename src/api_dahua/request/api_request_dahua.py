from typing import TypeVar, Generic

from src.api.api_request import ApiRequest
from src.api_dahua.response.api_response_dahua import ApiResponseDahua

T = TypeVar("T", bound=ApiResponseDahua)

class ApiRequestDahua(ApiRequest[T], Generic[T]):
    pass
