import os
import wget
import json
import requests
from bs4 import BeautifulSoup
from PIL import Image


def get_page_soup(url: str):
    """Make a BeautifulSoup object from a url"""
    res = requests.get(url)
    res.raise_for_status()
    return BeautifulSoup(res.content, 'html.parser')


def url_from_image_tag(image_tag):
    """Extract an image url from an html-style <img> element"""
    if image_tag.has_attr('data-src'):
        return image_tag['data-src']
    else:
        return image_tag['src']


def get_card_data_list():
    """Collect the image urls for each card in the game"""
    tt_url = "https://finalfantasy.fandom.com/wiki/Final_Fantasy_VIII_Triple_Triad_cards"
    soup = get_page_soup(tt_url)

    # isolate the tables in the webpage and prepare the output list
    table_list = list(soup.find_all('table', {'class': 'full-width FFVIII article-table'}))
    card_data_list = []

    for i, table in enumerate(table_list):  # iterate over the tables
        card_level = i + 1  # each table corresponds to a card level

        # iterate over rows in the table
        row_tags = list(table.find_all("tr"))[1:]
        for i, row in enumerate(row_tags):
            # each card has a placement (1-11) within it's level
            card_placement = i + 1

            # scrape the card_name from the row
            name_column_tag = row.find("span")
            card_name = name_column_tag["id"]

            # depending on the card, there may be two images (card_element, card_image) in the row
            image_tags = row.find_all("img")
            if len(image_tags) > 1:
                card_image_tag = image_tags[1]
                card_image_url = url_from_image_tag(card_image_tag)

                # we scrape the card_element from a substring of a tag attribute
                element_image_tab = image_tags[0]
                card_element = element_image_tab['alt'][12:-4]

            else:
                card_image_tag = image_tags[0]
                card_image_url = url_from_image_tag(card_image_tag)
                card_element = None

            # define the data packet
            card_data = {
                'name': card_name,
                'level': card_level,
                'placement': card_placement,
                'element': card_element,
                'image_url': card_image_url
            }
            card_data_list.append(card_data)

    return card_data_list


def download_card_images(card_data_list: list, directory: str):
    """Downloads images onto hard-drive"""
    for item in card_data_list:
        url = item['image_url']

        str_level = str(item['level']).zfill(2)
        str_placement = str(item['placement']).zfill(2)

        # https://towardsdatascience.com/how-to-download-an-image-using-python-38a75cfa21c
        wget.download(url, f'{directory}/{str_level}.{str_placement}.png')


# todo: extract common path names to a global variable
def data_to_json(card_data_list: list):
    """Dump collected data to JSON file"""
    with open('data_files/json', 'w') as json_file:
        json.dump(card_data_list, json_file)


data_list = get_card_data_list()
download_card_images(data_list, 'data_files')
data_to_json(data_list)
