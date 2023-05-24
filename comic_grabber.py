#!/usr/bin/python3
import argparse
import urllib.parse

import requests

from packages import shared_variables as sv
from packages.comicextra_processor import comic_extra
from packages.request_builder import soup_builder, hyphen_remove, issue_padding


def arg_parser():
    parser = argparse.ArgumentParser(description='Comic Search')
    parser.add_argument('-c', '--comic', help='Comic name to search', required=True)
    parser.add_argument('-a', '--alt', help='By default the script returns results from readcomicsonline, '
                                            'by passing the alt option you can select 1 of 2 alternative '
                                            'search providers 1. comicgalaxy 2. readcomiconline.li',
                        required=False)
    parser.add_argument('-i', '--img', help='Omits the image cropping process.', action='store_true')
    parser.add_argument('-b', '--ban', help='Omits the checking of the uploader watermark page', action='store_true')
    args = parser.parse_args()

    # Assign the values to the shared variables
    sv.search_term = urllib.parse.quote(args.comic)
    sv.img_option = args.img
    sv.ban_option = args.ban
    sv.alt_option = args.alt
    sv.comic_name = args.comic


arg_parser()

if sv.alt_option == '1':
    """
    With this option selected it returns the input search from comicextra.net
    """
    comic_extra(sv.comic_name, sv.search_term)

elif sv.alt_option == '2':
    print('Alternative search provider 2 selected')
    exit(0)

else:
    search_url = f'https://readcomicsonline.ru/search?query={sv.search_term}'

    search_response = requests.get(search_url, headers=sv.headers)
    search_data = search_response.json()

    comic_suggestions = search_data['suggestions']

    max_column_width = 65

    num_cols = 2
    num_results = len(comic_suggestions)
    num_rows = (num_results + num_cols - 1) // num_cols

    print(f'\nShowing results for : {sv.YELLOW}{sv.comic_name}{sv.RESET}\n')
    for row in range(num_rows):
        for col in range(num_cols):
            index = col * num_rows + row
            if index < num_results:
                comic_info = comic_suggestions[index]
                comic_name = comic_info['value']
                comic_name = hyphen_remove(comic_name)
                comic_data = comic_info['data']

                selection_number = (index + 1)
                formatted_string = issue_padding(selection_number, comic_name)
                padded_content = formatted_string.ljust(max_column_width)
                print(padded_content, end='')
        print()

    selection = input(f'\n{sv.YELLOW}Enter the number corresponding to the series you want (or "'
                      f'{sv.RESET}q{sv.YELLOW}" to quit): {sv.RESET}')

    if selection.lower() == 'q':
        print(f'{sv.YELLOW}Quitting the program...{sv.RESET}')
        exit()

    try:
        selection = int(selection)
        if 1 <= selection <= len(comic_suggestions):
            chosen_comic_data = comic_suggestions[selection - 1]['data']
            soup_builder(chosen_comic_data)
        else:
            print(f'\n{sv.RED}Invalid selection. Please enter a valid number.{sv.RESET}')
    except ValueError:
        print(f'\n{sv.RED}Invalid input. Please enter a valid number or "q" to quit.{sv.RESET}')
