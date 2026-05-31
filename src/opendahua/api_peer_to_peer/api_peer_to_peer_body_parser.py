import xmltodict

from opendahua.http.http_response_body import HttpResponseBody


class ApiPeerToPeerBodyParser:
    # Body constants.
    BODY_EMPTY = b""
    
    # Field constants.
    FIELD_BODY = "body"
    
    @classmethod
    def parse(cls, response_body: HttpResponseBody) -> dict:
        if response_body.get_http_response_body_bytes() == cls.BODY_EMPTY:
            return {}
        else:
            return xmltodict.parse(response_body.get_http_response_body_string())[cls.FIELD_BODY]
