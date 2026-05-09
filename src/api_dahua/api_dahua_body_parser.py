
class ApiDahuaBodyParser:
    # Separator constants.
    SEPARATOR_LINE_BODY = "\r\n"
    SEPARATOR_KEY_VALUE = "="

    @classmethod
    def determine_dict(cls, body_string: str) -> dict:
        response_dict = {}
        body_string_excluding_trailing_carriage_return = body_string.strip()
        
        all_line_body = body_string_excluding_trailing_carriage_return.split(cls.SEPARATOR_LINE_BODY)
        
        for line_body in all_line_body:
            key, value = line_body.split(cls.SEPARATOR_KEY_VALUE)
            
            response_dict[key] = value
        
        return response_dict
    