from abc import ABC, abstractmethod


class ApiResponse(ABC):
    @classmethod
    @abstractmethod
    def parse(cls, value: dict) -> ApiResponse:
        ...
        