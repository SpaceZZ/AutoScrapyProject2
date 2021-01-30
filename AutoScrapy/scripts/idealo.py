"""
v1 contact: fit.meal.planner@gmail.com

Script uses Selenium to scrap the following webpage
"""
import os
import time
import urllib.parse
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import csv
import random
from rich.console import Console
from rich.progress import track

############################################## START CONFIGURATION ####################################################

# webpage to scrape
webpage_target = r"https://www.idealo.de/preisvergleich/AllePartner/100I27-"
# Google Chrome profile to use
profile_uri = r"C:\Users\Admin\AppData\Local\Google\Chrome\User Data\Default"

# Google webdriver location (location of the exe)
webdriver_location = r"C:\Users\Admin\PycharmProjects\seleniumScraper\driver\chromedriver.exe"
############################################## END CONFIGURATION ####################################################

headers = ['short_name', 'name', 'url', 'email', 'address', 'country', 'website', 'contact', 'page_index']
requests_headers = {"accept-encoding": "gzip, deflate, br",
                    "accept-language": "en-US,en;q=0.9,pl-PL;q=0.8,pl;q=0.7,nl-NL;q=0.6,nl;q=0.5",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36", }
console = Console(color_system="windows")


class Item:
    """
    Class to hold the information about the scrape
    """

    def __init__(self):
        """
        Initializing the all the properties of the class
        """
        self.short_name = ""
        self.name = ""
        self.url = ""
        self.email = ""
        self.address = ""
        self.country = ""
        self.website = ""
        self.contact = ""
        self.index = ""

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
    dict_to_print = {'short_name': item.short_name,
                     'name': item.name,
                     'url': item.url,
                     'email': item.email,
                     'address': item.address,
                     'country': item.country,
                     'website': item.website,
                     'contact': item.contact,
                     'page_index': item.index
                     }

    with open("results_idealo.csv", 'a', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, delimiter='\t', fieldnames=headers)
        writer.writerow(dict_to_print)
        console.log(dict_to_print)


def scrape_shop_webpage(website_url):
    """
    Function uses requests to check the actual page with requests
    :param website_url:
    :type website_url:
    :return:
    :rtype:
    """
    resp = requests.get(website_url, timeout=10, allow_redirects=True, headers=requests_headers)
    if resp.status_code != 404:
        if resp.status_code == 429:
            while True:
                console.rule("Something wrong with request. Reset IP")
                time.sleep(5)
                resp = requests.get(website_url, timeout=10, allow_redirects=True, headers=requests_headers)
                if resp.status_code != 429:
                    break
        console.print(f"Found webpage {resp.url}")
        contact_page = resp.url
        fragments_url = urllib.parse.urlparse(contact_page)
        base_url = fragments_url.scheme + "://" + fragments_url.netloc
        return base_url, contact_page
    else:
        return "", website_url


def scrape_shop(driver, index):
    """
    Function scrapes shop website
    :return:
    :rtype:
    """
    # initialize object to be returned later
    item = Item()
    item.index = index

    # get short name
    try:
        short_name = driver.find_element_by_xpath('*//h2[@class="heading-1 mt-12"]/span')
        if short_name:
            item.short_name = short_name.text
    except Exception as ex:
        console.log(f"Error {ex}")

    # get name
    try:
        name = driver.find_elements_by_xpath('*//td[@class="shop-address"]')
        if name:
            item.name = name[0].text.split("\n")[0]
    except Exception as ex:
        console.log(f"Error {ex}")

    # get url
    try:
        item.url = driver.current_url
    except Exception as ex:
        console.log(f"Error {ex}")

    # get address
    try:
        address = driver.find_elements_by_xpath('*//td[@class="shop-address"]')
        if address:
            for _ in address:
                item.address += " " + _.text.strip()
            item.address.strip()
            item.address = item.address.replace(item.name, "").strip().replace("\n", "", 1)
    except Exception as ex:
        console.log(f"Error {ex}")

    # get country
    try:
        country = driver.find_elements_by_xpath('*//td[@class="shop-address"]')
        if country:
            item.country = country[-1].text.split("\n")[-1]
    except Exception as ex:
        console.log(f"Error {ex}")

    try:
        email = driver.find_elements_by_xpath('*//a[@class="link-3 test__contact_email"]')
        if email:
            item.email = email[0].text.split("\n")[0]
    except Exception as ex:
        console.log(f"Error {ex}")

    # webpage
    try:
        webpage = driver.find_element_by_xpath('*//td[@class="shop-meta"]/a[@class="link-3"]')
        if webpage:
            website_url = webpage.get_attribute("href")
            try:
                item.website, item.contact = scrape_shop_webpage(website_url)
            except Exception as ex:
                console.print(f"[red] Didnt succeed with scraping {item.name} at url {website_url}")
                item.contact = website_url
    except Exception as ex:
        console.log(f"Error {ex}")

    console.print("Scraped {} at {}".format(item.url, item))
    return item


def write_header():
    """
    Function writes header one time
    :return:
    :rtype:
    """
    if not os.path.isfile('results_idealo.csv'):
        with open("results_idealo.csv", 'a', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, delimiter='\t', fieldnames=headers)
            writer.writeheader()
            console.log("Wrote header to file")


def get_target_webpage(index):
    """
    Functions creates the url link for idealo.
    Basically first one is 0, second page is 15, third page is 30 etc
    :param index:
    :type index:
    :return:
    :rtype:
    """
    base_url = r"https://www.idealo.de/preisvergleich/AllePartner/100I27"
    if index == 1:
        return base_url
    else:
        new_url = base_url + "-" + str((index - 1) * 15)
        return new_url


def main():
    """
    Entry point for the script.
    :return:
    :rtype:
    """

    items = []
    results = []

    driver = get_driver()
    # driver.delete_all_cookies()

    write_header()

    start_page = 325
    end_page = 339

    console.rule("[bold red]Starting scraping")

    for index in range(start_page, end_page):
        wait_time = random.randint(3, 7)
        target = get_target_webpage(index)
        console.print("Waiting for loading the page {}".format(wait_time))
        WebDriverWait(driver, wait_time)

        time.sleep(wait_time)
        driver.get(target)

        results_page = driver.find_elements_by_xpath('*//a[@class="link-2"]')
        results_page_links = extract_links_for_page(results_page)

        for ind, result in (enumerate(results_page_links)):
            wait_time = random.randint(2, 4)
            console.print("Waiting for loading the SHOP {}".format(wait_time))

            time.sleep(wait_time)

            driver.get(result)
            item = scrape_shop(driver, index)
            console.print(
                f"Scraped {item.short_name}. At position {ind} of {len(results_page_links)}.\nAt {index} of {end_page}")
            write_to_file(item)

    console.log("Total results {}".format(len(items)))


def extract_links_for_page(results_page):
    """
    Extracts the links from the main pagination page
    :param results_page:
    :type results_page:
    :return:
    :rtype:
    """
    results = []
    for result in results_page:
        _text = result.text
        if "Startseite" not in _text:
            results.append(result.get_attribute("href"))
    return results


if __name__ == "__main__":
    main()
