from src.api.api_response import ApiResponse
from src.api_peer_to_peer.response.api_response_peer_to_peer import ApiResponsePeerToPeer


class ApiResponsePeerToPeerServerProbe(ApiResponsePeerToPeer):
    @classmethod
    def parse(cls, value: dict) -> ApiResponse:
        pass
