from datetime import datetime
import json
from colored import fg, bg, attr
from scraper import Scraper
import concurrent.futures
from threading import Lock
from datetime import datetime

scrape = Scraper('https://beonestore.x.yupoo.com')

# Reusable menu system
def create_menu(options):
    """Creates the menu for the program."""

    for i, option in enumerate(options):
        if option == 'spacer':
            print('')
        else:
            if options[i - 1] == 'spacer':
                i -= 1

            print(f'{fg(12)}{i + 1} {fg(8)}- {attr(0)}{option}')    
    choice = int(input('> '))
    return choice

def create_notification (success, message):
    """Creates a notification for the user."""
    
    return {'status': success, 'message': message, 'formatted': f'{fg(40 if success else 160)}{"Success" if success else "Error"} | {attr(0)}{message}'}
    

def fetch_albums (category):
    total = scrape.fetch_category_albums(category)

    return total

def progress_indicator(future):        # print(f'{tasks_completed}/{tasks_total} downloads complete, {tasks_total-tasks_completed} albums remain.', end='\r')

    global lock, tasks_total, tasks_completed
    # obtain the lock
    with lock:
        # update the counter
        tasks_completed += 1
        # report progress
        print(f'{fg(40)}{tasks_completed}/{tasks_total} {attr(0)}Albums Left, Downloaded {fg(40)}{future.result()} {fg(8)}images{attr(0)} | {datetime.now().strftime("%H:%M:%S")}', end='\r')
         
 
# create a lock for the counter
lock = Lock()
# total tasks we will execute
tasks_total = 0
# total completed tasks
tasks_completed = 0
# Main program
def main (notification=None):
    global tasks_total
    """A dummy docstring."""
    # Clear the screen and print the menu
    print('\n' * 100)
    
    # Print the notification if it exists
    if notification:
        print(f'{notification["formatted"]}\n')
    
    options = ['Fetch all Albums', 'Fetch all Categories', 'Download all Images from Albums', 'spacer', 'View your Categories']
    choice = create_menu(options)

    try:
        if choice == 1:
            with open('categories.json', 'r') as f:
                categories = json.load(f)
            
                # Loop through each category and download all the albums
                for category in categories:
                    total = fetch_albums(category['url'])
                    
                    # Print a notification after download in color
                    print(f'{fg(40)}{category["category"]} {fg(8)}- {attr(0)}Downloaded {fg(40)}{total} new {fg(8)}albums{attr(0)}')
                
                main(create_notification(True, 'All albums downloaded successfully'))
        elif choice == 2:
            scrape.download_categories()
            
            main(create_notification(True, 'All categories downloaded successfully'))
        elif choice == 3:
            # Fetch all albums from the manifest.json file
            with open('albums/manifest.json', 'r') as f:
                albums = json.load(f)
                
                tasks_total = len(albums)

                with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
                    futures = []
                    for album in albums:
                        futures.append(executor.submit(scrape.fetch_album_images, name=album['name'], album_id=album['url'].split('/')[-1]))
                    for future in futures:
                        future.add_done_callback(progress_indicator)
                    # for future in concurrent.futures.as_completed(futures):
                    #     print(future.result())
                    

                main(create_notification(True, 'All images downloaded successfully'))

            
    except Exception as e:
        main(create_notification(False, e))
        
        

if __name__ == '__main__':
    main()
