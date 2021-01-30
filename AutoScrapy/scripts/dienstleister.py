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
webpage_target = r"https://www.dienstleister-handel.de/dienstleister-suchen/Dienstleisterverzeichnis/Provider.html"
# Google Chrome profile to use
profile_uri = r"C:\Users\Admin\AppData\Local\Google\Chrome\User Data\Default"

# Google webdriver location (location of the exe)
webdriver_location = r"C:\Users\Admin\PycharmProjects\seleniumScraper\driver\chromedriver.exe"


############################################## END CONFIGURATION ####################################################


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
        self.category = []
        self.address = ""
        self.description = ""
        self.contact_person = ""
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
    headers = ['name', 'url', 'category', 'address', 'description', 'contact_person', 'website']
    dict_to_print = {'name': item.name,
                     'url': item.url,
                     'category': " ".join((item for item in item.category)),
                     'address': item.address,
                     'description': item.description,
                     'contact_person': item.contact_person,
                     'website': item.website
                     }

    with open("results_dienstleister_handel_de.csv", 'a', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, delimiter='\t', fieldnames=headers)
        writer.writeheader()
        writer.writerow(dict_to_print)
        print(dict_to_print)


def scrape_premium(driver):
    """
    Function scrapes premium website from the webpage
    :param driver:
    :type driver:
    :return:
    :rtype:
    """
    # initialize object to be returned later
    item = Item()

    # get name
    name = driver.find_element_by_xpath('*//div[@class="panel panel-light panel-special"]/h3')
    if name:
        item.name = name.text

    # get description
    description = driver.find_element_by_xpath('*//div[@class="media-body"]/p')
    if description:
        item.description = description.text

    # get categories
    categories = driver.find_elements_by_xpath('*//h1[contains(text(),"der Rubrik")]/a')
    if categories:
        for category in categories:
            item.category.append(category.text)

    # get url
    item.url = driver.current_url

    # get address
    address = driver.find_element_by_xpath('*//address')
    if address:
        p = address.find_elements_by_xpath('./p')
        for _ in p:
            item.address += " " + _.text.strip()
        item.address = item.address.replace(" vCard herunterladen", "")
        item.address.strip()

    # webpage
    webpage = address.find_element_by_xpath('.//a')
    if webpage:
        item.website = webpage.get_attribute("href")

    contact = driver.find_element_by_xpath('*//div[@class="media-body"]/address/p')
    if contact:
        item.contact_person = contact.text
    item.contact_person.strip()

    # go back in history
    print("Scraped {} \n {}".format(item.url, item))
    return item


def scrape_normal(driver):
    """
    Function scrapes premium website from the webpage
    :param driver:
    :type driver:
    :return:
    :rtype:
    """
    item = Item()

    name = driver.find_element_by_xpath('*//div[@class="panel panel-light panel-special"]/h3')
    if name:
        item.name = name.text

    # get categories
    categories = driver.find_elements_by_xpath('*//h1[contains(text(),"der Rubrik")]/a')
    if categories:
        for category in categories:
            item.category.append(category.text)

    # get address
    address = driver.find_element_by_xpath('*//address')
    if address:
        p = address.find_elements_by_xpath('./p')
        for _ in p:
            item.address += " " + _.text.strip()
        item.address = item.address.replace(" vCard herunterladen", "")
        item.address.strip()

    # webpage
    webpage = address.find_element_by_xpath('.//a')
    if webpage:
        item.website = webpage.get_attribute("href")

    return item


def main():
    """
    Entry point for the script.
    :return:
    :rtype:
    """
    items = []
    results_premium = []
    results_normal = []
    driver = get_driver()

    driver.get(webpage_target)

    elem = driver.find_element_by_name("tx_isapprovidercatalog_pi1[senden]")
    elem.click()
    print("Waiting for loading the page")
    WebDriverWait(driver, 3)

    y = 1000
    for timer in range(0, 50):
        driver.execute_script("window.scrollTo(0, " + str(y) + ")")
        y += 2000
        time.sleep(1)

    results_premium = driver.find_elements_by_xpath('*//div[@class="media search-result-premium"]/a')
    results_normal = driver.find_elements_by_xpath('*//div[@class="col-sm-6 search-result-default"]/p/a')

    results_premium = [result.get_attribute("href") for result in results_premium]
    results_normal = [result.get_attribute("href") for result in results_normal]

    for index, link in enumerate(results_premium):
        print("Waiting before scraping")
        WebDriverWait(driver, random.randint(1, 3))
        driver.get(link)
        WebDriverWait(driver, 1)
        print("Scraping the {} link of {} in premium results".format(index, len(results_premium)))
        item = scrape_premium(driver)
        items.append(item)

    for index, link in enumerate(results_normal):
        print("Waiting before scraping")
        WebDriverWait(driver, random.randint(1, 3))
        driver.get(link)
        WebDriverWait(driver, 1)
        print("Scraping the {} link of {} in normal results".format(index, len(results_normal)))
        item = scrape_normal(driver)
        items.append(item)

    for item in items:
        print(item)
        write_to_file(item)

    print("Total results {}".format(len(items)))


if __name__ == "__main__":
    main()
