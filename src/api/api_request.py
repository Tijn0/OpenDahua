from abc import ABC, abstractmethod
from typing import Type, TypeVar, Generic

from src.api.api_response import ApiResponse
from src.http.http_header import HttpHeader
from src.http.http_request import HttpRequest
from src.http.http_request_body import HttpRequestBody
from src.http.http_request_method import HttpRequestMethod
from src.object.url import Url

T = TypeVar("T", bound=ApiResponse)

class ApiRequest(ABC, Generic[T]):
    @abstractmethod
    def determine_endpoint(self) -> Url:
        ...
    
    
    @abstractmethod
    def get_request_method(self) -> HttpRequestMethod:
        ...
    
    
    @abstractmethod
    def determine_body_or_none(self) -> HttpRequestBody|None:
        ...
    
    
    def determine_all_header(self) -> list[HttpHeader]:
        return []
    
    
    def generate_http_request(self) -> HttpRequest:
        return HttpRequest(
            self.get_request_method(),
            self.determine_endpoint(),
            self.determine_all_header(),
            self.determine_body_or_none(),
        )


    @abstractmethod
    def get_response_class(self) -> Type[T]:
        ...

