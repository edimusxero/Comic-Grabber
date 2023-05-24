#!/usr/bin/python3
import os
import json
import packages.configuration_generator as cg

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
config_file = os.path.join(root_dir, 'config.json')

if not os.path.isfile(config_file):
    cg.__main__()


with open(config_file, 'r') as conf:
    config = json.load(conf)

search_term = ""
img_option = False
ban_option = False
alt_option = ""
comic_name = ""
mark_for_deletion = False

banned_dir = os.path.join(root_dir, 'banned')

"""
This requires tesseract OCR to be installed on your system.  Set the path to the location of the .exe or bin in
the config.json file
"""

tesseract_command_path = config['tesseract_location']

"""
Set the download folder location inside the config.json file
"""

download_folder = config['download_folder']

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}


# List of ANSII colors

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BLACK = "\033[0;30m"
BROWN = "\033[0;33m"
PURPLE = "\033[0;35m"
CYAN = "\033[0;36m"
LIGHT_GRAY = "\033[0;37m"
DARK_GRAY = "\033[1;30m"
LIGHT_RED = "\033[1;31m"
LIGHT_GREEN = "\033[1;32m"
LIGHT_BLUE = "\033[1;34m"
LIGHT_PURPLE = "\033[1;35m"
LIGHT_CYAN = "\033[1;36m"
LIGHT_WHITE = "\033[1;37m"
BOLD = "\033[1m"
RESET = '\033[0m'
