import requests
from bs4 import BeautifulSoup
import json
from colored import fg, bg, attr
import os
from concurrent.futures import ThreadPoolExecutor
import unicodedata
import re

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

class Scraper ():
    """Scrapes the webpage"""

    def __init__(self, url):
        self.url = url
        self.blacklist = ['/categories/', '/categories/276273', '/categories/276334']
        # self.soup = self.get_soup()
        
    def get_soup(self, path):
        r = requests.get(f'{self.url}{path}')
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup

    def fetch_existing_albums (self):
        # Read from the manifest.json file and return the albums, if it doesn't exist create an empty list
        try:
            with open('albums/manifest.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        
    
    def fetch_category_albums (self, category, category_name):
        # First fetch how many pages there are from pagination__jumpwrap
        soup = self.get_soup(category)
        
        # Get second to last button from pagination__buttons that includes a number
        last_page = soup.find('span', class_='categories__box-right-pagination-span').text.split(' / ')[-1]
        # Convert to int
        total_pages = int(last_page)
    
        # Loop through each page and fetch the albums
        new_albums_length = 0
        existing_albums = self.fetch_existing_albums()
        for page in range(1, total_pages + 1):
            soup = self.get_soup(f'{category}?page={page}')
            # Fetch the albums
            albums = soup.find_all('a', class_='album__main')
            
            for album in albums:
                # Fetch the album name
                name = album['title']
                # Fetch the album url
                url = album['href'].split('?')[0]
                
                category_dir = slugify(category_name)
                
                new_album = { 'name': name, 'url': url, 'category': category_dir }
                if new_album not in existing_albums:
                    new_albums_length += 1
                    existing_albums.append(new_album)

            # Write the new albums and old to the manifest.json file
            with open('albums/manifest.json', 'w') as f:
                json.dump(existing_albums, f)
                
        return new_albums_length
        
        
    
    def fetch_categories (self):
        soup = self.get_soup('/collections')
        
        # Fetch divs with class yupoo-collapse-header
        divs = soup.find_all('div', class_='yupoo-collapse-header')
        categories = []
        for div in divs:
            # Fetch the category name
            category = div.find('a').text
            # Fetch the category url
            url = div.find('a')['href']
            
            if url not in self.blacklist:
                categories.append({'category': category, 'url': url})

        return categories
        
    def download_categories (self):
        # Fetch the categories then write them to a json file named categories.json
        categories = self.fetch_categories()
        with open('categories.json', 'w') as f:
            # Convert categories to json string and write to file
            json.dump(categories, f)
    
    def fetch_existing_images (self, album_id, category):
        # Read from the images.json file and return the images, if it doesn't exist create an empty list
        try:
            directory = f'albums/{category}/{album_id}'
            if not os.path.exists(directory):
                os.makedirs(directory)

            with open(f'{directory}/images.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def download_images_threaded (self, image_array):
        with ThreadPoolExecutor(max_workers=9) as executor:
            executor.map(self.download_image, [image for image in image_array])
        
                        
    def download_image (self, image):
        # Download the image
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0',
            'Accept': 'image/avif,image/webp,*/*',
            'Accept-Language': 'en-GB,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://beonestore.x.yupoo.com/'
        }
        
        r = requests.get(image['src'], headers=headers)
        with open(f'albums/{image["category"]}/{image["album"]}/{image["name"]}', 'wb') as f:
            f.write(r.content)
        # print(f'{fg(4)}Downloaded {fg(166)}{image["name"]}{attr(0)}')
    
    def fetch_album_images (self, name, category, album_id):
        # Convert name string to a suitable filename
        dir = slugify(name)
        
        # Fetch the album images and write them to a json file named images.json
        soup = self.get_soup(f'/albums/{album_id}?uid=1')
        images = soup.find_all('img', class_='image__img')

        # Create a list of images
        existing_images = self.fetch_existing_images(dir, category)
        images_list = []
        for image in images:
            image_dict = { 'src': f'https://photo.yupoo.com{image["data-path"]}', 'album': dir, 'category': category, 'name': image['data-path'].split('/')[-1] }
            
            if image_dict not in existing_images:
                images_list.append(image_dict)
                existing_images.append(image_dict)

        
        
        # # Ask for users confirmation to download the images
        # print(f'\n{fg(166)}Download {fg(4)}{len(images_list)} new {fg(166)}images?{attr(0)}')
        # choice = input('[y/n] ')
        # if choice == 'y':
            # Create a directory for the album
        self.download_images_threaded(images_list)
        
        with open(f'albums/{category}/{dir}/images.json', 'w') as f:
            json.dump(existing_images, f)
        
        return len(images_list)