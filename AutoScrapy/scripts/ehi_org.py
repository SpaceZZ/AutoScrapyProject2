"""
v1 contact: fit.meal.planner@gmail.com

Script uses Selenium to scrap the following webpage
"""
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import pandas as pd
import csv
import time
import random

############################################## START CONFIGURATION ####################################################

# webpage to scrape
webpage_target = r"https://www.ehi.org/de/das-institut/unsere-mitglieder?page_id=194&posts_page="
# Google Chrome profile to use
profile_uri = r"C:\Users\Admin\AppData\Local\Google\Chrome\User Data\Default"

# Google webdriver location (location of the exe)
webdriver_location = r"C:\Users\Admin\PycharmProjects\seleniumScraper\driver\chromedriver.exe"
############################################## END CONFIGURATION ####################################################

headers = ['name', 'url', 'phone', 'email', 'address', 'website']


class Item:
    """
    Class to hold the information about the scrape
    """

    def __init__(self):
        """
        Initializing the all the properties of the class
        """
        self.name = ""
        self.url = ""
        self.phone = ""
        self.email = ""
        self.address = ""
        self.website = ""

    def __str__(self):
        """
        Method returns the data scraped
        :return:
        :rtype:
        """
        return str(vars(self))


def get_driver():
    """
    Create chrome driver for scraping
    :return:
    :rtype:
    """
    opts = Options()
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36")
    opts.add_argument("--user-data-dir={}".format(profile_uri))
    opts.add_argument("--disable-extensions")
    return webdriver.Chrome(executable_path=webdriver_location, options=opts)


def write_to_file(item):
    """
	Methods writes completed object to the file
	:param item:
	:return:
	"""
    dict_to_print = {'name': item.name,
                     'url': item.url,
                     'phone': item.phone,
                     'email': item.email,
                     'address': item.address,
                     'website': item.website
                     }

    with open("results_ehi_org.csv", 'a', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, delimiter='\t', fieldnames=headers)
        writer.writerow(dict_to_print)
        print(dict_to_print)


def scrape_card(card, current_url):
    """
    Function scrapes premium website from the webpage
    :param card:
    :type card:
    :return:
    :rtype:
    """
    # initialize object to be returned later
    item = Item()

    # get name
    name = card.find_element_by_xpath('.//h4')
    if name:
        item.name = name.text

    # get url
    item.url = current_url

    # get address
    address = card.find_elements_by_xpath('.//div[@class="col-md-4"]//p[position()>1]')
    if address:
        for _ in address:
            item.address += " " + _.text.strip()
        item.address.strip()

    phone = card.find_element_by_xpath('.//div[@class="col-md-8 border-none"]/p[2]')
    if phone:
        item.phone = phone.text

    email = card.find_element_by_xpath('.//div[@class="col-md-8 border-none"]/p[4]')
    if email:
        item.email = email.text

    # webpage
    webpage = card.find_element_by_xpath('.//div[@class="col-md-8 border-none"]/p[last()]/a')
    if webpage:
        item.website = webpage.get_attribute("href")
    if item.website == "http:":
        item.website = ""

    print("Scraped {} \n {}".format(item.url, item))
    return item


def write_header():
    """
    Function writes header one time
    :return:
    :rtype:
    """
    with open("results_ehi_org.csv", 'a', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, delimiter='\t', fieldnames=headers)
        writer.writeheader()
        print("Wrote header to file")


def main():
    """
    Entry point for the script.
    :return:
    :rtype:
    """
    items = []
    results = []

    driver = get_driver()

    for index in range(1, 29):
        wait_time = random.randint(2, 5)
        target = webpage_target + str(index)
        print("Waiting for loading the page {}".format(wait_time))
        WebDriverWait(driver, wait_time)
        driver.get(target)
        results_cards = driver.find_elements_by_xpath('*//div[@class="media-body col-md-9"]')
        for result in results_cards:
            items.append(scrape_card(result, driver.current_url))

    write_header()
    for item in items:
        print(item)
        write_to_file(item)

    print("Total results {}".format(len(items)))


if __name__ == "__main__":
    main()
