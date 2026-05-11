from datetime import datetime

class DateTimeDahua(datetime):
    # Format constants.
    FORMAT_DAHUA_DATETIME_STRING = "%Y-%m-%dT%H:%M:%SZ"
    
    def get_datetime_dahua_string(self) -> str:
        return self.strftime(self.FORMAT_DAHUA_DATETIME_STRING)
