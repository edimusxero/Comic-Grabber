import os
import re

import cv2
import pytesseract
from PIL import Image
from alive_progress import alive_bar

from packages import shared_variables as sv

"""
Checks if the tesseract_command_path variable is set in the shared_variables file.
If not, it enables the skip cropping process
"""
if not sv.tesseract_command_path:
    sv.img_option = True
else:
    pytesseract.pytesseract.tesseract_cmd = sv.tesseract_command_path


def collect_image_files(folder_path):
    """
    Builds a list of image files to process_images
    """
    image_files = []
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']  # Add more valid extensions if needed

    for file_name in os.listdir(folder_path):
        file_extension = os.path.splitext(file_name)[1].lower()
        if file_extension in valid_extensions:
            image_files.append(f'{folder_path}/{file_name}')

    return image_files


def extract_numeric_part(filename):
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else 0


def crop_image(image_path, crop_height):
    """
    Various image files from readcommicsonline.ru have a black bar watermark at
    the bottom.  This function crops that part out of the image.
    """
    image = Image.open(image_path)
    width, height = image.size
    new_height = height - crop_height
    cropped_image = image.crop((0, 0, width, new_height))
    cropped_filename = os.path.splitext(image_path)[0] + '_cropped.jpg'
    cropped_image.save(cropped_filename)
    image.close()
    os.remove(image_path)
    return cropped_filename


def image_processor_check(comic_folder):
    image_list = collect_image_files(comic_folder)

    if sv.img_option:
        print(f'{sv.BROWN}Skipping cropping process{sv.RESET}\n')
    else:
        process_images(image_list)

    if sv.ban_option:
        print(f"{sv.BROWN}Skipping ban check{sv.RESET}\n")
    else:
        image_verifier(image_list)


def process_images(image_list):
    """
    This function runs the images through tesseract.
    """

    custom_config = '--oem 3 --psm 6'

    with alive_bar(len(image_list),
                   bar='fish',
                   spinner='bubbles',
                   title=f'{sv.YELLOW}Processing images{sv.RESET}'
                   ) as bar:
        for img in image_list:
            image = Image.open(img)
            text = pytesseract.image_to_string(image, config=custom_config)
            image.close()

            bar()  # Increment the progress bar

            if 'Read more FREE comics on ReadComicOnline' in text:
                print(f"\nCropping : {sv.YELLOW}{img}{sv.RESET}\n")
                cropped_image = crop_image(img, 50)
                os.rename(cropped_image, img)
    return


def compare_images(image1, image2):
    if image1 is None or image2 is None:
        # Either image1 or image2 is None
        # Handle the case where either image is None
        return None

    # Check the shapes of the images
    if image1.shape != image2.shape:
        # Resize image1 to match the shape of image2
        resized_image1 = cv2.resize(image1, (image2.shape[1], image2.shape[0]))
    else:
        resized_image1 = image1

    return ((resized_image1 - image2) ** 2).mean()


def image_verifier(image_files):
    print()
    with alive_bar(len(image_files),
                   bar='fish',
                   spinner='bubbles',
                   title=f'{sv.YELLOW}Checking for bans :{sv.RESET}'
                   ) as bar:
        for img in image_files:
            image = cv2.imread(img)

            # Loop through each reference image
            reference_files = os.listdir(sv.banned_dir)
            for reference_file in reference_files:
                if sv.mark_for_deletion:
                    break

                # Load the reference image
                reference_path = os.path.join(sv.banned_dir, reference_file)
                reference = cv2.imread(reference_path)
                ssim_score = compare_images(image, reference)

                if ssim_score is None:
                    print(f'{sv.RED}Failed to process Images{sv.RESET}')
                if ssim_score < 0.5:
                    if reference_file == 'error.jpg':
                        sv.mark_for_deletion = True

                    print(f"\n Deleting Image : {sv.YELLOW}{img}\n{sv.RESET}"
                          f"Reference : {sv.LIGHT_RED}{reference_file}{sv.RESET}\n"
                          f"SSIM Score : {sv.BROWN}{ssim_score}{sv.RESET}\n\n")
                    os.remove(img)
                bar()
    return
