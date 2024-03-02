import asyncio
from kasa import Discover

my_devices = asyncio.run(Discover.discover())
for addr, dev in my_devices.items():
    asyncio.run(dev.update())
    print(f"{addr} >> {dev}")