import os
import threading

import requests
from bs4 import BeautifulSoup
from natsort import natsorted

from packages import shared_variables as sv, downloader_functions as df
from packages.zip_functions import extract_issue_number
from packages.column_builder import build_column_layout


def download_issue(threaded_issue):
    th_images_url = f'{threaded_issue[1]}/full'
    th_comic_name = df.clean_file_path_name(threaded_issue[0])
    print(f'\n{sv.YELLOW}{th_comic_name}{sv.RESET} is preparing to download\n')
    download_cx_images(extract_issue_number(th_comic_name), th_images_url)


def grab_issues(url):
    issue_response = requests.get(url)
    soup = BeautifulSoup(issue_response.content, 'html.parser')
    print()

    issue_list = []

    table_body = soup.find('tbody', id='list')
    if table_body:
        table_rows = table_body.find_all('tr')
        for row in table_rows:
            link = row.find('a')
            if link:
                issue_title = link.text.strip()
                issue_url = link['href']
                issue_list.append((df.clean_file_path_name(issue_title), issue_url))

    sorted_results = natsorted(issue_list, key=lambda x: x[1])

    num_columns = None

    if len(sorted_results) > 10:
        num_columns = 2

    if len(sorted_results) > 20:
        num_columns = 3

    if num_columns:
        num_rows = (len(sorted_results) + num_columns - 1) // num_columns

        max_title_length = max(len(sorted_results[i][0]) for i in range(len(sorted_results)))
        column_width = max_title_length + 5  # Add additional padding between columns

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

    selection = input(f'\n{sv.YELLOW}Enter the issue you want to download '
                      f'(or "{sv.RESET}q{sv.YELLOW}" to quit, '
                      f'"{sv.RESET}a{sv.YELLOW}" for all) : {sv.RESET}')

    if selection.lower() == 'q':
        print(f'{sv.YELLOW}Quitting the program...{sv.RESET}')
        # Add any necessary cleanup or exit code here if needed
        exit()

    if selection.lower() == 'a':
        print(f'\n{sv.BROWN}Downloading all issues{sv.RESET}')
        # Add any necessary cleanup or exit code here if needed

        # Create a list to hold the threads
        threads = []

        # Iterate over the sorted results and create a thread for each issue
        for single_issue in sorted_results:
            # Create a thread for each issue and pass the download_issue function as the target
            thread = threading.Thread(target=download_issue, args=(single_issue,))
            threads.append(thread)

            # Start the thread
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

    else:
        try:
            selection = int(selection)
            if 1 <= selection <= len(sorted_results):
                chosen_comic_data = sorted_results[selection - 1]
                images_url = f'{chosen_comic_data[1]}/full'
                comic_name = df.clean_file_path_name(chosen_comic_data[0])
                download_cx_images(extract_issue_number(comic_name), images_url)
            else:
                print(f'\n{sv.RED}Invalid selection. Please enter a valid number.{sv.RESET}')
        except ValueError:
            print(f'\n{sv.RED}Invalid input. Please enter a valid number or "{sv.RESET}q{sv.RED}" to quit.{sv.RESET}')


def download_cx_images(comic_download_name, issue_url):
    full_download_path = f'{sv.download_folder}/{comic_download_name}'

    if os.path.exists(f'{full_download_path}.cbz'):
        print(f'{sv.YELLOW}Comic has already been downloaded.{sv.RESET}')
        exit(0)

    if not os.path.exists(full_download_path):
        # Create the folder
        os.makedirs(full_download_path)
    else:
        print(f"Folder already exists : {sv.YELLOW}{full_download_path}{sv.RESET}")

    try:
        response = requests.get(issue_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        title_element = soup.find('title')
        title = title_element.text.strip()

        if title == 'Error, 404 not found!':
            print('Error - Page not found')
            exit(0)

        else:
            chapter_images = soup.find_all('img', class_="chapter_img")
            if not chapter_images:
                print(f'{title} : not yet released')
                exit(0)

            else:
                img_urls = []

                for chapter_imgs in soup.find_all('img', class_="chapter_img"):
                    img_url = chapter_imgs['src'].strip()
                    img_urls.append(img_url)

            df.download_images(full_download_path, img_urls)
            return

    except requests.exceptions.RequestException:
        pass


def comic_extra(search_string, user_search):
    print(f'\nComicextra search results for: {sv.YELLOW}{search_string}{sv.RESET}\n')
    search = f'https://comicextra.net/comic-search?key={user_search}&page=1'

    response = requests.get(search, headers=sv.headers)
    alt1_soup = BeautifulSoup(response.content, 'html.parser')

    urls = [search]

    divs = alt1_soup.find_all('div', class_='general-nav')

    for div in divs:
        span = div.find('span', class_='button-content')
        if span and span.text.strip() == '1':
            links = div.find_all('a')
            for link in links:
                url = link['href']
                if url not in urls:
                    urls.append(url)

    issues = []  # List to store the issue titles and URLs

    for alt_link in urls:
        issue_builder = requests.get(alt_link, headers=sv.headers)
        alt_master_response = BeautifulSoup(issue_builder.content, 'html.parser')

        divs = alt_master_response.find_all('div', class_='cartoon-box')

        for div in divs:
            h3 = div.find('h3')
            if h3:
                issue_title = h3.text.strip()
                if issue_title == 'Not found':
                    print(f"No results found for : {sv.YELLOW}{sv.comic_name}{sv.RESET}\n")
                    exit(0)
                issue_url = h3.find('a')['href']
                issues.append((issue_title, issue_url))

    # Returns the layout of our output
    build_column_layout(issues)

    selection = input(f'\n{sv.YELLOW}Enter the number corresponding to the series you want '
                      f'(or "{sv.RESET}q{sv.YELLOW}" to quit) :{sv.RESET} ')

    if selection.lower() == 'q':
        print(f'\n{sv.YELLOW}Quitting the program...{sv.RESET}')
        exit()

    try:
        selection = int(selection)

        if 1 <= selection <= len(issues):
            chosen_comic_data = issues[selection - 1]
            selected_url = chosen_comic_data[1]
            grab_issues(selected_url)
            # Perform the desired action with the selected URL
        else:
            print(f'{sv.RED}Invalid selection.{sv.RESET}')
    except ValueError:
        print(f'\n{sv.RED}Invalid input. Please enter a valid number.{sv.RESET}')
