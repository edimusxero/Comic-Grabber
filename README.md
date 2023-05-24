# Comic-Grabber
Python scripts for downloading comics from readcomicsonline.to and comicextra.net

This script is for ripping comics from readcomicsonline.ru and comicextra.net.

In addition to downloading the images for the selected comic it also processes the downloaded images, crops out the black bar "Read more at" text that some uploaded comic files have and removes any of the commonly used ripper pages (generally added to the end of the comic.)

Once processed, the folder is converted into a .cbz file.

Usage 

python3 comic_grabber.py -c <comic name> [-a / --alt 1 (to search comicextra) | -i / --img (to ignore file cropping process) | -b / --ban (to ignore checking watermark pages)
  
 <img width="600" alt="search example" src="https://github.com/edimusxero/Comic-Grabber/assets/15164376/ea092127-8778-428a-899c-7cc386da47a0">


 <img width="600" alt="issue output" src="https://github.com/edimusxero/Comic-Grabber/assets/15164376/7ee2b792-28fd-4a06-bcd5-b4e5b6d99630">

  
  
This does require the installation of Tesseract-OCR if you want to take advantage of the cropping process.
  
A config file will be created upon first run to set your downloads directory and tesseract-ocr path.
  
Keep in mind, this is still a work in progress.  Would love to add a gui to it or implement some other functions.  I am planning on adding the ability to rip from readcomiconline.li as well.
  
Note -- Add any of the water mark uploader files (such as zone, empire etc.) to the banned folder, I am sure there are plenty more files out there that I have yet to stumble across
