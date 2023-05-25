#!/usr/bin/python3
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup
from natsort import natsorted

from packages import shared_variables as sv
from packages.downloader_functions import grab_issue_pages
from packages.zip_functions import extract_issue_number
import packages.downloader_functions as df


# Builds a request and returns soup
def soup_builder(comic_series):
    search_url = f'https://readcomicsonline.ru/comic/{comic_series}'
    search_response = requests.get(search_url, headers=sv.headers)
    soup = BeautifulSoup(search_response.content, 'html.parser')

    issue_releases = soup.find_all(class_='chapters')

    chapter_list = []

    for individual_release in issue_releases:
        for comic_issue in individual_release.find_all('li'):
            issue_link = comic_issue.find('a')
            issue_url = issue_link['href']
            issue_title = issue_link.text.strip()
            issue_title = extract_issue_number(issue_title)
            chapter_list.append((issue_title, issue_url))

    sorted_results = natsorted(chapter_list, key=lambda x: x[1])

    print()
    num_columns = None

    if len(sorted_results) > 10:
        num_columns = 2

    if len(sorted_results) > 20:
        num_columns = 3

    if num_columns:
        num_rows = (len(sorted_results) + num_columns - 1) // num_columns

        max_title_length = max(len(sorted_results[i][0]) for i in range(len(sorted_results)))
        column_width = max_title_length + 20  # Add additional padding between columns

        for i in range(num_rows):
            for j in range(num_columns):
                index = i + j * num_rows
                if index < len(sorted_results):
                    issue_title = sorted_results[index][0]
                    padding = df.issue_padding(index + 1, issue_title)
                    output = "{:<{}}".format(padding, column_width)
                    print(output, end='')
            print()
    else:
        for index, issue in enumerate(sorted_results, 1):
            issue_title = issue[0]
            padding = df.issue_padding(index, issue_title)
            print(padding)

    # Prompt the user for input
    selection = input(f'\n{sv.YELLOW}Enter the number of the comic issue you wish to download '
                      f'(enter "{sv.RESET}q{sv.YELLOW}" to quit or '
                      f'"{sv.RESET}a{sv.YELLOW}" to download all) : {sv.RESET}')

    if selection.lower() == 'q':
        print(f'\n{sv.YELLOW}Quitting the program...{sv.RESET}')
        # Add any necessary cleanup or exit code here if needed
        exit()

    if selection.lower() == 'a':
        print(f'\n{sv.BROWN}Downloading all available issues{sv.RESET}\n')

        with ThreadPoolExecutor(max_workers=10) as executor:
            download_tasks = [executor.submit(grab_issue_pages, single_issue[1], single_issue[0]) for
                              single_issue in sorted_results]

            for future in download_tasks:
                future.result()
    else:
        df.image_downloader_function(selection, sorted_results)
