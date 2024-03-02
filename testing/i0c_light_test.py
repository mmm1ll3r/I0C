import os
import asyncio
import requests
from dotenv import load_dotenv
from kasa import SmartLightStrip

# load env variables
load_dotenv()

# get IP of Smart Light Strip from env
strip_ip = os.getenv("STRIP_IP")
strip = SmartLightStrip(strip_ip)

async def light_test_onoff():
    try:
        # Update the light strip state
        await strip.update()

        # Turn off the light if it's currently on
        if strip.is_on:
            await strip.turn_off()

        # Check a website
        url = "http://example.com"
        response = requests.get(url)
        print(f"Response from {url}: {response.status_code}")

        # If responase is 200, light up and then turn off after 2 seconds
        if response.status_code == 200:
            await strip.set_hsv(0, 100, 50)
            await strip.set_brightness(100)
            await strip.turn_on()
            await asyncio.sleep(2)
            await strip.turn_off()

    except requests.RequestException as e:
        print(f"Error checking website: {e}")
    except Exception as e:
        print(f"Error controlling light strip: {e}")

if __name__ == "__main__":
    asyncio.run(light_test_onoff())