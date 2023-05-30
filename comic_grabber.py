#!/usr/bin/python3
import argparse
import urllib.parse

import requests

from packages import shared_variables as sv, downloader_functions as df
from packages.column_builder import build_column_layout
from packages.comicextra_processor import comic_extra
from packages.request_builder import soup_builder
from packages.readcomiconline_processor import search_rco


def arg_parser():
    parser = argparse.ArgumentParser(description='Comic Search')
    parser.add_argument('-c', '--comic', help='Comic name to search', required=True)
    parser.add_argument('-a', '--alt', help='By default the script returns results from readcomicsonline, '
                                            'by passing the alt option you can select 1 of 2 alternative '
                                            'search providers 1. comicgalaxy 2. readcomiconline.li',
                        required=False)
    parser.add_argument('-x', '--max', help='Max returned results. Helpful when searching '
                                            'readcomiconline.li due to the large amounts of data returned',
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
    sv.max_results = args.max


arg_parser()

if sv.alt_option == '1':
    """
    With this option selected it returns the input search from comicextra.net
    """
    comic_extra(sv.comic_name, sv.search_term)

elif sv.alt_option == '2':
    """
    With this option selected it returns the input search from readcomiconline.li
    """
    search_rco(sv.search_term)

else:
    search_url = f'https://readcomicsonline.ru/search?query={sv.search_term}'

    search_response = requests.get(search_url, headers=sv.headers)
    search_data = search_response.json()

    issue_info = []

    comic_suggestions = search_data['suggestions']

    if len(comic_suggestions) == 0:
        print(f'\nNothing found for : {sv.YELLOW}{sv.comic_name}{sv.RESET}\n')
        exit(0)

    print(f'\nShowing results for : {sv.YELLOW}{sv.comic_name}{sv.RESET}\n')
    for row in comic_suggestions:
        comic_name = row['value']
        comic_name = df.hyphen_remove(comic_name)
        comic_data = row['data']
        issue_info.append((comic_name, comic_data))

    if sv.max_results:
        build_column_layout(issue_info[:int(sv.max_results)])
    else:
        build_column_layout(issue_info)

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
