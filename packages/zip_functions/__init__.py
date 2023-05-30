#!/usr/bin/python3
import os
import re
import shutil
import zipfile

from packages import shared_variables as sv
import packages.downloader_functions as df


def zip_folder(folder_path):
    zip_path = f'{folder_path}.cbz'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))
    try:
        shutil.rmtree(folder_path)
        print(f"\n{sv.YELLOW}Folder removed successfully.{sv.RESET}")
        if sv.mark_for_deletion:
            os.remove(zip_path)
            comic_archive = os.path.basename(zip_path)
            print(f'\n{sv.RED}Removed {sv.YELLOW}{comic_archive}{sv.RESET} {sv.RED}due to empty image files{sv.RESET}')

        if os.path.isfile(zip_path):
            print(f'\n{zip_path} creation was successful\n')
    except OSError as e:
        print(f"Error: {e}")


def extract_issue_number(comic_title):
    # Extract the issue number using regular expressions
    if " Issue " in comic_title:
        comic_title = comic_title.replace(" Issue ", " ")
    match = re.search(r'#(\d+)', comic_title)
    if match:
        issue_number = int(match.group(1))

        if issue_number is not None:
            # Apply zero padding based on the value
            if issue_number < 10:
                padded_number = f'00{str(issue_number)}'
            elif 10 <= issue_number < 100:
                padded_number = f'0{str(issue_number)}'
            else:
                padded_number = f'{str(issue_number)}'

            # Replace the issue number in the title with the padded number
            return re.sub(r'#(\d+)', f'#{padded_number}', df.hyphen_remove(comic_title))
    else:
        return re.sub(r'#', '', comic_title)
