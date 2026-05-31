from typing import TypeVar, Generic

from opendahua.api.api_request import ApiRequest
from opendahua.api_dahua.response.api_response_dahua import ApiResponseDahua

T = TypeVar("T", bound=ApiResponseDahua)

class ApiRequestDahua(ApiRequest[T], Generic[T]):
    pass
