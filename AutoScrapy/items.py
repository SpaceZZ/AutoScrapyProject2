# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

# eurocist item
class EuroCisItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    street = scrapy.Field()
    zip_code = scrapy.Field()
    city = scrapy.Field()
    country = scrapy.Field()
    telephone = scrapy.Field()
    fax = scrapy.Field()
    # list of categories
    categories = scrapy.Field()
    # list of company websites
    website = scrapy.Field()
    # list of emails
    email = scrapy.Field()
    # description
    desc = scrapy.Field()
    #hall
    location = scrapy.Field()
    products = scrapy.Field()
    url = scrapy.Field()

class EhiSiegelItem(scrapy.Item):
    name = scrapy.Field()
    street = scrapy.Field()
    zip_code = scrapy.Field()
    city = scrapy.Field()
    country = scrapy.Field()
    categories = scrapy.Field()
    website = scrapy.Field()
    desc = scrapy.Field()
    url = scrapy.Field()
    Vertretungsberechtigter = scrapy.Field()
    Registereintrag = scrapy.Field()
    UStIdNr = scrapy.Field()

class t3nItem(scrapy.Item):
    name = scrapy.Field()
    street = scrapy.Field()
    zip_code = scrapy.Field()
    city = scrapy.Field()
    country = scrapy.Field()
    telephone = scrapy.Field()
    email = scrapy.Field()
    desc = scrapy.Field()
    categories = scrapy.Field()
    website = scrapy.Field()
    url = scrapy.Field()
    linkedin = scrapy.Field()
    twitter = scrapy.Field()
    facebook = scrapy.Field()