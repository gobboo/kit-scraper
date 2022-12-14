# Kit Scraper
- [Kit Scraper](#kit-scraper)
  - [Description](#description)
  - [Prerequisites](#prerequisites)
  - [Installing](#installing)
  - [Usage](#usage)
  - [License](#license)


## Description
This is a scraper for this [Kit Image Site](https://beonestore.x.yupoo.com/). It uses BeautifulSoup and Multithreading to scrape their entire website's categories & albums to download over 18,000+ images in under 30 minutes. Not useful by nature, was made for a friend to use as a tool to download images for a project.



## Prerequisites
* [Python 3.10](https://www.python.org/)
* [pip](https://pip.pypa.io/en/stable/)

## Installing
First extract the contents of the zip file to a folder.

Next open up a terminal and run the following command:

```bash
cd location/of/extraction/folder
```
**Note:** Change `location/of/extraction/folder` to the exact location of where you extracted the contents of the zip file.


Once inside the folder, run the following to install the needed modules:
```bash
pip install -r requirements.txt
```
**or**
```bash
python -m pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

To begin, first **Download All categories**, after this you can **Download All Albums**. Finally you can **Download All Images**.
This may take long and it may hinder your Internet performance, so please be patient.

All data is stored within JSON files, if removed or corrupted, the scraper will recreate them and refetch all data, it uses these files to know what already exists so it doesn't redowload the same data so it'll only look for new content.

## License

[MIT](https://opensource.org/licenses/MIT)

