#!/usr/bin/python3
import os
import re

import requests
from alive_progress import alive_bar
from bs4 import BeautifulSoup

from packages import shared_variables as sv
from packages.image_processor import image_processor_check
from packages.zip_functions import zip_folder


def hyphen_remove(deformed_name):
    fixed_name = re.sub(r"-(?=\))", "", deformed_name)
    return fixed_name.replace('&amp;', '&')


def issue_padding(issue_result, padded_name):
    if '#full' in padded_name.lower():
        padded_name = re.sub('#', '', padded_name)

    if issue_result < 10:
        number_string = f'  {issue_result}'
    elif 10 <= issue_result < 100:
        number_string = f' {issue_result}'
    else:
        number_string = str(issue_result)

    return f'{number_string}. {padded_name}'


def clean_file_path_name(filename):
    filename = re.sub(r'[<>:"/|?*]', ' ', filename)
    filename = re.sub(r'\s+', ' ', filename)
    return filename


def grab_issue_pages(issue_url, download_title):
    search_response = requests.get(issue_url, headers=sv.headers)
    soup = BeautifulSoup(search_response.content, 'html.parser')
    imagecnt_div = soup.find('div', id='all')

    img_elements = imagecnt_div.find_all("img", {"class": "img-responsive"})
    image_urls = [img['data-src'].strip() for img in img_elements]

    comic_download_name = clean_file_path_name(download_title)
    full_download_path = f'{sv.download_folder}/{comic_download_name}'

    if os.path.exists(f'{full_download_path}.cbz'):
        print(f'{sv.YELLOW}Comic has already been downloaded.{sv.RESET}')
        exit(0)

    if not os.path.exists(full_download_path):
        # Create the folder
        os.makedirs(full_download_path)
    else:
        print(f"{sv.LIGHT_RED}Folder already exists : {sv.YELLOW}{full_download_path}{sv.RESET}")

    collected_images = []
    with alive_bar(len(image_urls),
                   bar='fish',
                   spinner='bubbles',
                   title=f'{sv.CYAN}Downloading images{sv.RESET} :'
                   ) as bar:
        for comic_image, img_url in enumerate(image_urls, start=1):
            try:
                img_data = requests.get(img_url).content
                img_name = f"page{comic_image}.jpg"
                img_path = f'{full_download_path}/{img_name}'

                with open(img_path, 'wb') as file:
                    file.write(img_data)
                collected_images.append(img_path)
            except Exception as e:
                print(f"\n{sv.RED}Error downloading or processing {img_url}: {e}{sv.RESET}")

            bar()
    print(f'{sv.BROWN}\n{os.path.basename(download_title)}{sv.RESET} : '
          f'{sv.RESET}successfully downloaded\n')
    image_processor_check(full_download_path)
    zip_folder(full_download_path)


def download_images(folder_path, image_list):
    """
    Downloads the images to a folder for processing
    """
    with alive_bar(len(image_list),
                   bar='fish',
                   spinner='bubbles',
                   title=f'{sv.CYAN}Downloading images {sv.RESET}:'
                   ) as bar:
        for i, img_url in enumerate(image_list, start=1):
            try:
                img_data = requests.get(img_url).content
                img_name = f"page{i}.jpg"
                img_path = os.path.join(folder_path, img_name)

                with open(img_path, 'wb') as file:
                    file.write(img_data)
            except Exception as e:
                print(f"{sv.RED}Error downloading or processing {img_url}: {e}{sv.RESET}")

            bar()
    image_processor_check(folder_path)
    print(f"\n{sv.YELLOW}Creating CBZ file {sv.RESET}:")
    zip_folder(folder_path)


def image_downloader_function(input_selection, sorted_chapters):
    # Convert the input to an integer
    try:
        selected_number = int(input_selection)

        # Check if the selected number is within the valid range
        if 1 <= selected_number <= len(sorted_chapters):
            issue_url = sorted_chapters[selected_number - 1][0]
            issue_title = sorted_chapters[selected_number - 1][1]
            issue_title = hyphen_remove(issue_title)
            print(f'\n{sv.BROWN}{issue_title}{sv.RESET} is preparing to download\n')
            grab_issue_pages(issue_url, issue_title)
        else:
            print(f'{sv.RED}Invalid selection.{sv.RESET}')
    except ValueError:
        print(f'\n{sv.RED}Invalid input. Please enter a valid number or "{sv.RESET}q{sv.RED}" to quit.{sv.RESET}')
