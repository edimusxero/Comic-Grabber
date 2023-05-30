import os

from natsort import natsorted

from packages import downloader_functions as df
from packages.column_builder import build_column_layout
from packages.zip_functions import extract_issue_number
from packages.readcomiconline_single_issue import *


def grab_issues(selected_series):
    full_url = f'https://readcomiconline.li{selected_series}'
    response = requests.get(full_url, headers=sv.headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', class_='listing')

    rows = table.find_all('tr')

    issues_list = []

    for row in rows[1:]:  # Skip the first row (header row)
        columns = row.find_all('td')
        if len(columns) == 2:
            title = columns[0].text.strip()
            url = columns[0].find('a')['href']
            long_url = f'https://readcomiconline.li{url}'
            issues_list.append((df.clean_file_path_name(title), long_url))

    sorted_results = natsorted(issues_list, key=lambda x: x[1])

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
                      f'(or "{sv.RESET}q{sv.YELLOW}" to quit.{sv.RESET}')

    if selection.lower() == 'q':
        print(f'{sv.YELLOW}Quitting the program...{sv.RESET}')
        # Add any necessary cleanup or exit code here if needed
        exit()

    else:
        try:
            selection = int(selection)
            if 1 <= selection <= len(sorted_results):
                chosen_comic_data = sorted_results[selection - 1]
                images_url = f'{chosen_comic_data[1]}/full'
                comic_name = df.clean_file_path_name(chosen_comic_data[0])
                print(f'\n{sv.YELLOW}{comic_name}{sv.RESET} is preparing to download\n')

                scrape_issues = populate_images(images_url)

                full_download_path = f'{sv.download_folder}/{extract_issue_number(comic_name)}'

                if os.path.exists(f'{full_download_path}.cbz'):
                    print(f'{sv.YELLOW}Comic has already been downloaded.{sv.RESET}')
                    exit(0)

                if not os.path.exists(full_download_path):
                    # Create the folder
                    os.makedirs(full_download_path)
                else:
                    print(f"Folder already exists : {sv.YELLOW}{full_download_path}{sv.RESET}")

                decoded_image_urls = []

                for decoded_url in scrape_issues:
                    decoded_image_urls.append(beau(decoded_url))

                df.download_images(full_download_path, decoded_image_urls)
            else:
                print(f'\n{sv.RED}Invalid selection. Please enter a valid number.{sv.RESET}')

        except ValueError:
            print(f'\n{sv.RED}Invalid input. Please enter a valid number or "{sv.RESET}q{sv.RED}" to quit.{sv.RESET}')


def rco_single_issue(selected_issue):
    return selected_issue


def search_rco(search_term):
    rco_search_url = 'https://readcomiconline.li/Search/Comic'

    payload = {
        'keyword': search_term
    }

    response = requests.post(rco_search_url, headers=sv.headers, data=payload)
    soup = BeautifulSoup(response.content, 'html.parser')
    list_comics = soup.find_all('div', class_='list-comic')

    rco_search_results = []

    for comic in list_comics:
        items = comic.find_all('div', class_='item')
        for item in items:
            title_match = re.search(r'<p class="title">(.*?)</p>', item['title'])
            if title_match:
                title = title_match.group(1)
                url = item.find('a')['href']
                rco_search_results.append((title, url))

    if len(rco_search_results) == 0:
        print(f'\nNothing found for : {sv.YELLOW}{search_term}{sv.RESET}\n')
        exit(0)

    print(f'\nShowing results for: {sv.YELLOW}{search_term}{sv.RESET}\n')

    if sv.max_results:
        build_column_layout(rco_search_results[:int(sv.max_results)])
    else:
        build_column_layout(rco_search_results)

    selection = input(f'\n{sv.YELLOW}Enter the number corresponding to the series you want '
                      f'(or "{sv.RESET}q{sv.YELLOW}" to quit) :{sv.RESET} ')

    if selection.lower() == 'q':
        print(f'\n{sv.YELLOW}Quitting the program...{sv.RESET}')
        exit()

    try:
        selection = int(selection)

        if 1 <= selection <= len(rco_search_results):
            chosen_comic_data = rco_search_results[selection - 1]
            selected_url = chosen_comic_data[1]
            grab_issues(selected_url)
            # Perform the desired action with the selected URL
        else:
            print(f'{sv.RED}Invalid selection.{sv.RESET}')
    except ValueError:
        print(f'\n{sv.RED}Invalid input. Please enter a valid number.{sv.RESET}')
