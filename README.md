# OpenDahua
![PyPI - Version](https://img.shields.io/pypi/v/opendahua)
 
Python SDK for interacting with Dahua NVRs (Network Video Recorders) over their proprietary peer-to-peer protocol.

## Installation
You can install OpenDahua with your favorite python package manager!

```text
pip install opendahua
```
or
```text
uv add opendahua
```

## Usage
> [!WARNING]
> Within the ```async with DahuaNVR(xxx) as nvr:``` block you should use async for all IO operations. The peer-to-peer connection might die if you don't do this.

```python
import asyncio
from datetime import datetime, timedelta

from opendahua import DahuaNVR


async def main() -> None:
    async with DahuaNVR("SERIAL_NUMBER_HERE", "USERNAME_HERE", "PASSWORD_HERE") as nvr:
        all_video = await nvr.get_all_video(
            channel=1,
            time_start=datetime.now() - timedelta(days=1),
        )
        
        for video in all_video:
            path = nvr.download_video(video, "videos/")
            
            # Example: videos/ExampleNVR_ch1_20260601135935_20260601140002.dav
            print(f"Video path: {path}")
        
if __name__ == "__main__":
    asyncio.run(main())
```


## Special thanks to
- [khoanguyen-3fc/dh-p2p](https://github.com/khoanguyen-3fc/dh-p2p): The reverse engineering work and proof-of-concept that make this project possible.
