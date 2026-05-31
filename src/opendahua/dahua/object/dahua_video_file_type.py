from enum import Enum


class DahuaVideoFileType(Enum):
    MP4 = "mp4"
    DAV = "dav"
    
    def __str__(self):
        return self.value
