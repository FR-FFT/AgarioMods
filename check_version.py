import requests
import json
import os
import sys

def save_run_status(status):
    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        print(f'new_version={str(status).lower()}', file=fh)

def get_latest_version(app_id, country="us"):
    """Fetch the latest app version from the iTunes Search API."""
    url = f"https://itunes.apple.com/lookup?id={app_id}&country={country}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data["resultCount"] > 0:
            return data["results"][0]["version"]
        else:
            raise ValueError("App not found on the App Store.")
    else:
        response.raise_for_status()

def read_stored_version(file_path):
    """Read the stored app version from a file."""
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return file.read().strip()
    return None

def write_stored_version(file_path, version):
    """Write the latest app version to a file."""
    with open(file_path, "w") as file:
        file.write(version)

def main():
    APP_ID = "995999703" # Agar.io
    VERSION_FILE = "version.txt"

    try:
        print("Checking for the latest version...")
        latest_version = get_latest_version(APP_ID)
        print(f"Latest version on the App Store: {latest_version}")

        stored_version = read_stored_version(VERSION_FILE)
        if stored_version:
            print(f"Stored version: {stored_version}")

        if stored_version != latest_version:
            print("New version detected! Updating...")
            write_stored_version(VERSION_FILE, latest_version)
            print("Version file updated.")
            save_run_status(True)
        else:
            print("No updates detected. You're up to date!")
            save_run_status(False)

    except Exception as e:
        print(f"Error: {e}")
        save_run_status(False)

if __name__ == "__main__":
    main()
