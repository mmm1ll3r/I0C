import os
import json
import asyncio
import logging
import requests
from dotenv import load_dotenv
from ioc_light import control_light

# logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logfile_notifs.log"),  # Save logs to a file
        logging.StreamHandler()  # Output logs to console
    ]
)

# Grab the variables from .env file
load_dotenv()
VT_API_KEY = os.getenv("VT_API_KEY")
NOTIFICATION_TAG = os.getenv("NOTIFICATION_TAG")

# Create the VirusTotalQuery class + functions to get notifications
class VirusTotalQuery:
    def __init__(self, filter_query, limit, output_dir):
        self.filter_query = filter_query
        self.limit = limit
        self.output_dir = output_dir

    async def query_notifs(self):
        url = 'https://www.virustotal.com/api/v3/ioc_stream'
        headers = {
            'X-Apikey': VT_API_KEY,
            'accept': 'application/json'
        }
        params = {
            'filter': self.filter_query,
            'limit': self.limit
        }

        try:
            response = requests.get(url, headers=headers, params=params, stream=True)
            if response.status_code == 200:
                response_data = response.json()
                notifications = response_data.get('data', [])  # Extract 'data' array
                new_notifications = []  # List to store new notifications
                for notification in notifications:
                    notification_date = notification.get("context_attributes", {}).get("notification_date", "")
                    if notification_date:
                        filename = os.path.join(self.output_dir, f"{notification_date}.json")
                        # Check if file already exists
                        if not os.path.exists(filename):
                            # Save notification as JSON file
                            with open(filename, 'w') as f:
                                json.dump(notification, f, indent=4)
                            new_notifications.append(os.path.basename(filename))  # Add filename to new notifications list
                # Write list of new notifications to 'new' file
                with open('new', 'a') as new_file:
                    for item in new_notifications:
                        new_file.write("%s\n" % item)
                if new_notifications:
                    logging.info(f"Saved {len(new_notifications)} new notifications to {self.output_dir}.")
                else:
                    logging.info("No new notifications found.")
            else:
                logging.error(f"Failed to fetch data. Status code: {response.status_code}")
        except Exception as e:
            logging.error("An error occurred:", exc_info=True)

async def main():
    filter_query = f'notification_tag:{NOTIFICATION_TAG}'
    limit = 40  # Max 40
    output_dir = 'notifications'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    vt_query = VirusTotalQuery(filter_query, limit, output_dir)
    await vt_query.query_notifs()
    
    # Now run the IoC light script
    await control_light()

if __name__ == "__main__":
    asyncio.run(main())