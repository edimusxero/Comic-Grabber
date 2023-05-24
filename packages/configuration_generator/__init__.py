#!/usr/bin/python3
import json
import os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
config_path = os.path.join(root_dir, 'config.json')


def __main__():
    if os.path.isfile(config_path):
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)

        if 'download_folder' not in config and 'tesseract_location' not in config:
            print("Incomplete configuration found. Editing variables...")

            download_folder = input("Enter the download folder path: ")
            tesseract_location = input("Enter the tesseract path: ")

            config['download_folder'] = download_folder
            config['tesseract_location'] = tesseract_location

            with open(config_path, 'w') as config_file:
                json.dump(config, config_file, indent=4)

            print("Configuration updated successfully.")
    else:
        print("Configuration file not found. Creating new configuration...")

        download_folder = input("Enter the download folder path: ")
        tesseract_location = input("Enter the tesseract path: ")

        config = {
            "download_folder": download_folder,
            "tesseract_location": tesseract_location
        }

        with open(config_path, 'w') as config_file:
            json.dump(config, config_file, indent=4)

        print("Configuration created successfully.")
