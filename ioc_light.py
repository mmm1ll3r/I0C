import os
import json
import random
import asyncio
import logging
from dotenv import load_dotenv
from kasa import SmartLightStrip

# logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logfile_light.log"),  # Save logs to a file
        logging.StreamHandler()  # Output logs to console
    ]
)

# load env variables
load_dotenv()

# get IP of light strip from env
strip_ip = os.getenv("STRIP_IP")
strip = SmartLightStrip(strip_ip)

# Set up HSV color values, tag values, for each variable
A_hsv = (123, 100, 90)  # lime green - "Redline"
A_tag = "Redline"
B_hsv = (174, 100, 90)  # sea green "Creal Stealer"
B_tag = "Creal Stealer"
C_hsv = (225, 100, 90)  # blue - "StealC"
C_tag = "StealC"
D_hsv = (265, 100, 90)  # purple - "PureLog Stealer"
D_tag = "PureLog Stealer"
E_hsv = (322, 100, 90)  # fushia - "RisePro Stealer"
E_tag = "RisePro Stealer"
F_hsv = (204, 100, 90)  # light blue - (other - windows)
F_tag = "windows"
G_hsv = (286, 100, 90)  # pink - (other, non windows, likely macho)

## other options: MetaStealer, Vidar,
## QuasarStealer, Redline, UmbralStealer
## RHADAMANTHYS, LummaC
## Raccoon, Amos... 

async def control_light():
    # sometimes the light connection is spotty, so implemented a retry
    max_retries = 3
    retry_delay = 1  #s
    retry_count = 0

    while retry_count < max_retries:
        try:
            logging.info("Updating the light strip state...")
            # Update the light strip state
            await strip.update()

            # Turn off the light if it's currently on
            if strip.is_on:
                logging.info("Turning off the light...")
                await strip.turn_off()
                
            # Check if "new" file exists and get the number of items
            if os.path.exists("new"):
                logging.info("New items found. Reading...")
                with open("new", "r") as file:
                    new_items = file.readlines()
                    num_items = len(new_items)
                    logging.info(f"Number of new items: {num_items}")

                    # Calculate total run time
                    # Doing this so I don't step on my notifs_req.py cron job
                    # Have timliness limitations based on VT API quota
                    total_run_time = 570  # 9m30s
                    total_run_time -= num_items * 2  # Subtract 2s per notif light up
                    
                    remaining_time = total_run_time
                    
                    # Loop through the new items in reverse order, earliest first
                    for item in reversed(new_items):
                        filename = item.strip()

                        # Get specific data from corresponding JSON file
                        with open(os.path.join('notifications', filename), "r") as json_file:
                            notification_data = json.load(json_file)
                            malware_names = get_malware_names(notification_data)
                            type_tags = get_filetype_tags(notification_data)

                        # Light up based on malware_names or type_tags
                        hsv = det_hsv(malware_names, type_tags, filename)

                        # Set light color
                        await strip.set_hsv(*hsv)
                        await strip.set_brightness(100)
                        # Alert light on for 2s
                        await strip.turn_on()
                        await asyncio.sleep(2)
                        # Turn off the light
                        logging.info("Turning off.")
                        await strip.turn_off()
                        
                        # Calculate sleep time til next notification
                        # Spacing these out, for art
                        sleep_time = calculate_sleep_time(remaining_time, num_items)
                        await asyncio.sleep(sleep_time)

                        # Subtract wait time from total run time
                        remaining_time -= sleep_time
                        logging.info(f"Til next alerts: {sleep_time}, Remaining on run: {remaining_time}s")

                    # Delete the "new" file
                    os.remove("new")
                    logging.info("New file removed.")
            else:
                logging.info("No new items found.")

            # If all operations are successful, break out of the retry loop
            break

        except Exception as e:
            logging.error(f"Error controlling light strip: {e}")
            logging.info(f"Retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)
            retry_count += 1
    else:
        logging.error("Failed to control light strip after multiple retries.")

def get_malware_names(data):
    malware_names = []
    attributes = data.get("attributes", {})
    sandbox_verdicts = attributes.get("sandbox_verdicts", {})
    for verdict in sandbox_verdicts.values():
        malware_names.extend(verdict.get("malware_names", []))
    return malware_names

def get_filetype_tags(data):
    attributes = data.get("attributes", {})
    type_tags = attributes.get("type_tags", [])
    return type_tags

def det_hsv(malware_names, type_tags, filename):
    if A_tag in malware_names:
        logging.info(f"Displaying {A_tag} alert color for {filename}.")
        return A_hsv
    elif B_tag in malware_names:
        logging.info(f"Displaying {B_tag} alert color for {filename}.")
        return B_hsv
    elif C_tag in malware_names:
        logging.info(f"Displaying {C_tag} alert color for {filename}.")
        return C_hsv
    elif D_tag in malware_names:
        logging.info(f"Displaying {D_tag} alert color for {filename}.")
        return D_hsv
    elif E_tag in malware_names:
        logging.info(f"Displaying {E_tag} alert color for {filename}.")
        return E_hsv
    elif F_tag in type_tags:
        logging.info(f"Displaying {F_tag}/other alert color for {filename}.")
        return F_hsv
    else:
        logging.info(f"Displaying other - non-windows alert color for {filename}.")
        return G_hsv

def calculate_sleep_time(remaining_time, num_items):
    # Calculate the maximum wait time interval based on the remaining time
    max_wait_time = remaining_time / num_items
    # Generate a random fraction of the maximum wait time
    random_fraction = random.uniform(0.5, 1.5) # This seemed to look good
    # Calculate the sleep time by scaling the maximum wait time with the random fraction
    sleep_time = max_wait_time * random_fraction
    # Cap the sleep time to ensure it's not longer than the remaining time
    sleep_time = min(sleep_time, remaining_time)
    return sleep_time

if __name__ == "__main__":
    asyncio.run(control_light())