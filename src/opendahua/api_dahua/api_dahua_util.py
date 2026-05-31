from datetime import datetime

class ApiDahuaUtil:
    # Format constants.
    FORMAT_DATETIME_DAHUA_STRING = "%Y-%m-%dT%H:%M:%SZ"
    
    @classmethod
    def determine_datetime_dahua_string(cls, datetime: datetime):
        return datetime.strftime(cls.FORMAT_DATETIME_DAHUA_STRING)
