# apod_downloader.py
import requests
import os
from datetime import datetime, timedelta

APOD_URL = "https://api.nasa.gov/planetary/apod"
OUTPUT_DIR = "apod_images"

def download_apod_image(api_key, date=None, hd=False):
    """
    Downloads the APOD image for a given date.

    Args:
        api_key (str): Your NASA API key.
        date (str, optional): Date in YYYY-MM-DD format. Defaults to today.
        hd (bool, optional): If True, requests the high-definition image. Defaults to False.
    """
    params = {"api_key": api_key}
    if date:
        params["date"] = date
    if hd:
        params["hd"] = "True"

    try:
        response = requests.get(APOD_URL, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes

        apod_data = response.json()

        if apod_data["media_type"] == "image":
            image_url = apod_data["hdurl"] if hd and "hdurl" in apod_data else apod_data["url"]
            image_title = apod_data["title"].replace(" ", "_")
            file_extension = os.path.splitext(image_url)  # Extract extension from URL
            filename = os.path.join(OUTPUT_DIR, f"{image_title}_{apod_data['date']}{file_extension}")

            os.makedirs(OUTPUT_DIR, exist_ok=True)

            with open(filename, "wb") as f:
                image_response = requests.get(image_url)
                image_response.raise_for_status()
                f.write(image_response.content)
            print(f"Downloaded APOD: {image_title} to {filename}")

        elif apod_data["media_type"] == "video":
            print(f"APOD for {date if date else 'today'} is a video. URL: {apod_data['url']}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching APOD: {e}")
    except KeyError:
        print("Error: Missing 'url' or 'hdurl' in APOD response.")

if __name__ == "__main__":
    nasa_api_key = os.getenv("NASA_API_KEY")

    if not nasa_api_key:
        print("Error: NASA_API_KEY environment variable not set.")
        exit(1)

    # Example usage (can be customized)
    download_apod_image(nasa_api_key, hd=True)
    # Download images for the past 5 days
    # for i in range(5):
    #     target_date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
    #     download_apod_image(nasa_api_key, date=target_date)
```## 3. Requirements file (`requirements.txt`)

