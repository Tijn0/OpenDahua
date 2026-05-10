from dataclasses import dataclass


@dataclass(frozen=True)
class ApiDahuaMediaFileFinderIdentifier:
    _media_file_identifier_int: int
    
    def get_media_file_identifier_int(self) -> int:
        return self._media_file_identifier_int
    
    def __str__(self):
        return str(self.get_media_file_identifier_int())
    