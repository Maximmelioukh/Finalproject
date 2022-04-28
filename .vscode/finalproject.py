""" 
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py image_dir_path [apod_date]

Parameters:
  image_dir_path = Full path of directory in which APOD image is stored
  apod_date = APOD image date (format: YYYY-MM-DD)

History:
  Date        Author    Description
  2022-03-11  J.Dalby   Initial creation
  2022-04-28  Maxim Melioukh Edits made
"""
from sys import argv, exit
from datetime import datetime, date
from hashlib import sha256
from os import path
import ctypes
import re
import requests
import sqlite3

def main():

    # Determine the paths where files are stored
    image_dir_path = get_image_dir_path()
    db_path = path.join(image_dir_path, 'apod_images.db')

    # Get the APOD date, if specified as a parameter
    apod_date = get_apod_date()

    # Create the images database if it does not already exist
    create_image_db(db_path)

    # Get info for the APOD
    apod_info_dict = get_apod_info(apod_date)
    
    # Download today's APOD
    image_url = apod_info_dict["url"]
    image_msg = download_apod_image(image_url)
    image_sha256 = sha256(image_msg).hexdigest()
    image_size = len(requests.get(image_url).content)
    image_path = get_image_path(image_url, image_dir_path)

    # Print APOD image information
    print_apod_info(image_url, image_path, image_size, image_sha256)

    # Add image to cache if not already present
    if not image_already_in_db(db_path, image_sha256):
        save_image_file(image_msg, image_path)
        add_image_to_db(db_path, image_path, image_size, image_sha256)

    # Set the desktop background image to the selected APOD
    set_desktop_background_image(image_path)

def get_image_dir_path():#complete
    """
    Validates the command line parameter that specifies the path
    in which all downloaded images are saved locally.

    :returns: Path of directory in which images are saved locally
    """
    if len(argv) >= 2:
        dir_path = argv[1]
        if path.isdir(dir_path):
            print("Images directory:", dir_path)
            return dir_path
        else:
            print('Error: Non-existent directory', dir_path)
            exit('Script execution aborted')
    else:
        print('Error: Missing path parameter.')
        exit('Script execution aborted')

def get_apod_date():#complete
    """
    Validates the command line parameter that specifies the APOD date.
    Aborts script execution if date format is invalid.

    :returns: APOD date as a string in 'YYYY-MM-DD' format
    """    
    if len(argv) >= 3:
        # Date parameter has been provided, so get it
        apod_date = argv[2]

        # Validate the date parameter format
        try:
            datetime.strptime(apod_date, '%Y-%m-%d')
        except ValueError:
            print('Error: Incorrect date format; Should be YYYY-MM-DD')
            exit('Script execution aborted')
    else:
        # No date parameter has been provided, so use today's date
        apod_date = date.today().isoformat()
    
    print("APOD date:", apod_date)
    return apod_date

def get_image_path(image_url, dir_path):#complete
    image_name = re.search('https://apod.nasa.gov/apod/image/[0-9]+/(.*)', image_url).group(1)
    
    """
    Determines the path at which an image downloaded from
    a specified URL is saved locally.

    :param image_url: URL of image
    :param dir_path: Path of directory in which image is saved locally
    :returns: Path at which image is saved locally
    """
    return path.join(dir_path, image_name)

def get_apod_info(date):#complete
    
    """
    Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    :param date: APOD date formatted as YYYY-MM-DD
    :returns: Dictionary of APOD info
    """
    print("Getting NASA's APOD info...", end='')
    api_key = "api_key=Eqlg4nZAYdQNygU2sSxxJhwk1l4eN5DgJhrnvgqE"
    day_month_year = "date="+ date
    response = requests.get("https://api.nasa.gov/planetary/apod?" + day_month_year + "&" + api_key) 

    if response.status_code == 200:
        print('Success!')
        return response.json()
    else:
        print('Failed, Response code:', response.status_code) 
    return {"todo" : "TODO"}

def print_apod_info(image_url, image_path, image_size, image_sha256):#complete
    """
    Prints information about the APOD

    :param image_url: URL of image
    :param image_path: Path of the image file saved locally
    :param image_size: Size of image in bytes
    :param image_sha256: SHA-256 of image
    :returns: None
    """
    print("This is the image URL!" + image_url)
    print("This is the path of the image file saved locally on your device!" + image_path)
    print("This is the size of the file in bytes!" , image_size)
    print("This is the SHA-256 of the image!" + image_sha256)

    return #TODO

def download_apod_image(image_url):#complete
    """
    Downloads an image from a specified URL.

    :param image_url: URL of image
    :returns: Response message that contains image data
    """
    print("Downloading image from url...", end='')
   
    response = requests.get(image_url)

    if response.status_code == 200:
        print('Success!')
        return response.content
    else:
        print('Failed, Response code:', response.status_code)


def save_image_file(image_msg, image_path):#complete 
    """
    Extracts an image file from an HTTP response message
    and saves the image file to disk.

    :param image_msg: HTTP response message
    :param image_path: Path to save image file
    :returns: None
    """
    print("Saving image path...")
    with open(image_path, 'wb') as file:
            file.write(image_msg)
    print("Successfully saved to", image_path)

def create_image_db(db_path):#complete
    """
    Creates an image database if it doesn't already exist.

    :param db_path: Path of .db file
    :returns: None
    """
    connection = sqlite3.connect(db_path)
    curser = connection.cursor()
    tablemaker = """CREATE TABLE IF NOT EXISTS images (
        path text PRIMARY KEY,
        size integer NOT NULL,
        hash text NOT NULL);"""
    curser.execute(tablemaker)
    connection.commit()
    connection.close()

def add_image_to_db(db_path, image_path, image_size, image_sha256):#complete
    """
    Adds a specified APOD image to the DB.

    :param db_path: Path of .db file
    :param image_path: Path of the image file saved locally
    :param image_size: Size of image in bytes
    :param image_sha256: SHA-256 of image
    :returns: None
    """
    connection = sqlite3.connect(db_path)
    curser = connection.cursor()
    print("This image was not found in the Database! It will be added shortly!")
    add_image = """INSERT INTO images (
        path, size, hash) VALUES (?,?,?)"""
    new_image = (image_path, image_size, image_sha256)
    curser.execute(add_image, new_image)
    connection.commit()
    connection.close()

def image_already_in_db(db_path, image_sha256):#complete
    """
    Determines whether the image in a response message is already present
    in the DB by comparing its SHA-256 to those in the DB.

    :param db_path: Path of .db file
    :param image_sha256: SHA-256 of image
    :returns: True if image is already in DB; False otherwise
    """ 
    connection = sqlite3.connect(db_path)
    curser = connection.cursor()
    all_images = curser.execute("SELECT * FROM images;")
    for image in all_images:
        if image[2]== image_sha256:
            print("This image is already in the database silly goose!")
            return True 
    connection.commit()
    connection.close()

def set_desktop_background_image(image_path):#complete
    """
    Changes the desktop wallpaper to a specific image.

    :param image_path: Path of image file
    :returns: None
    """
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 0)

main()