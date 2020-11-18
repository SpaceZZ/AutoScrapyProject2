import scrapy
from AutoScrapy.items import MyDealzDeItem
from scrapy.http import HtmlResponse
import urllib.parse
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9,pl-PL;q=0.8,pl;q=0.7,nl-NL;q=0.6,nl;q=0.5',
    'content-type': 'application/json',
}


class MyDealz(scrapy.Spider):
    """
    Spider to get the data from the eurocis
    """
    name = "MyDealzSpider"

    custom_settings = {
        # 'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': 'False',
        'FEED_URI': 'MyDealz.csv',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
    }
    # allowed_domains = ['mydealz.de']
    start_urls = ["https://www.mydealz.de/angebote/a-d",
                  "https://www.mydealz.de/angebote/e-g",
                  "https://www.mydealz.de/angebote/h-k",
                  "https://www.mydealz.de/angebote/l-o",
                  "https://www.mydealz.de/angebote/p-s",
                  "https://www.mydealz.de/angebote/t-w",
                  "https://www.mydealz.de/angebote/x-z",
                  "https://www.mydealz.de/angebote/0-9",
                  ]

    def make_requests_from_url(self, url):
        """
        Override the default start urls to not allow to redirect, coz some ad shit is popping up
        :param url:
        :type url:
        :return:
        :rtype:
        """
        return scrapy.Request(url, dont_filter=True,
                              meta={
                                  'dont_redirect': True,
                                  'handle_httpstatus_list': [301, 302]
                              })

    def parse(self, response):
        """
        Method looks for the shop links

        :param response: the fully downloaded webpage
        :return: the iterator over the categories links
        """
        list_of_shops_selector = response.xpath(".//*/a[@class='linkPlain tGrid width--all-12']")
        category_url = response.request.url
        for shop in list_of_shops_selector:
            name = shop.xpath('./*/span/text()').extract_first().strip()
            redirect_url = shop.xpath('./@href').extract_first().strip()
            yield scrapy.Request(url=redirect_url, callback=self.parse_data, meta={'name': name,
                                                                                   'category_url': category_url})

    def parse_data(self, response):
        """
        Method parses the data for each shop
        :param response:
        :return:
        """
        shop_name = response.meta['name']
        category_url = response.meta['category_url']
        shop_url = response.request.url
        url = response.xpath('./*//a[contains(text(),"Seite")]/@href').extract_first()

        # create item to be passed
        item = MyDealzDeItem()
        item['name'] = shop_name
        item['category_url'] = category_url
        item['url'] = shop_url

        yield scrapy.Request(url=url, callback=self.parse_webpage, meta={'item': item})

    def parse_webpage(self, response):
        """
        parse webpage, needs to be smart
        :param response:
        :type response:
        :return:
        :rtype:
        """
        item = response.meta['item']
        print("Request url {}, actual requested url {}".format(item['url'], response.request.url))
        # website url
        item['website_url'] = response.request.url

        # get website title
        item['website_title'] = self.get_webpage_title(response)
        # get description from website
        item['website_desc'] = self.get_webpage_description(response)

        # get keywords from website
        item['keywords'] = self.get_webpage_keywords(response)

        # try to get email and phones
        item['email'] = self.extract_email(response)
        item['phone'] = self.extract_phone(response)

        if not item['email']:
            # try to get contact info
            # check if there is kontakt link on the page
            item = self.check_webpage_for_contact_details(item, response, "impressum")

            if not item['email']:
                try:
                    # try Contact
                    item = self.check_webpage_for_contact_details(item, response, "kontakt")

                except Exception as e:
                    print("Exception", e)

        if item['email']:
            item['email'] = item['email'].replace("(at)", "@")
        yield item

    def get_webpage_keywords(self, response):
        """
        Method tried to find the keywords of the webpage
        :param response:
        :type response:
        :return:
        :rtype:
        """
        tags = response.xpath('//*/meta[@property="keywords"]/@content').extract_first()
        tags1 = response.xpath('//*/meta[@name="keywords"]/@content').extract_first()
        if tags:
            return tags.strip()
        elif tags1:
            return tags1.strip()
        else:
            tags = response.xpath('//*/meta[@itemprop="keywords"]/@content').extract_first()
            if tags:
                return tags.strip()
            else:
                return ""

    def get_webpage_description(self, response):
        """
        Method tries to find the description of the webpage
        :param response:
        :type response:
        :return:
        :rtype:
        """
        desc = response.xpath('//*/meta[@itemprop="description"]/@content').extract_first()
        desc1 = response.xpath('//*/meta[@name="description"]/@content').extract_first()
        desc_length = 50
        if desc1:
            return desc1[:desc_length].strip()
        else:
            if desc:
                return desc[:desc_length].strip()
            else:
                desc = response.xpath('//*/meta[@property="description"]/@content').extract_first()
                if desc:
                    return desc[:desc_length].strip()
                else:
                    return ""

    def check_webpage_for_contact_details(self, item, response, suffix):
        """
        Check if there is specific keyword link in the webpage
        :param item:
        :type item:
        :param response:
        :type response:
        :param suffix:
        :type suffix:
        :return:
        :rtype:
        """
        check_contact = response.xpath('//*/a[contains(@href,{})]/@href'.format("\"" + suffix + "\"")).extract_first()
        if check_contact:
            full_url = urllib.parse.urljoin(response.request.url, check_contact)
            resp = requests.get(full_url, timeout=15)
            if resp.status_code != 404:
                print("Found webpage {}", full_url)
                item['contact_page'] = full_url
                raw_response = HtmlResponse(url=full_url, body=resp.content, encoding='utf-8')
                item['email'] = self.extract_email(raw_response)
                item['phone'] = self.extract_phone(raw_response)
                return item
            else:
                return item
        else:
            return item

    def extract_email(self, response):
        """
        Return extracted email
        :param response:
        :type response:
        :return:
        :rtype:
        """
        emails = response.xpath('//*/a[contains(@href,"mailto:")]/text()').extract()
        if emails:
            emails = [email.strip() for email in emails if email]
            # join only non empty strings
            return ",".join(filter(None, emails)).strip()
        else:
            emails = response.xpath('//*/a[contains(@href,"mailto:")]/@href').extract()
            if emails:
                emails = [email.strip().replace("mailto:", "") for email in emails if email]
                return ",".join(filter(None, emails)).strip()
            else:
                emails = response.xpath('//*/p[contains(text(),"E-Mail:")]/text()').extract()
                if emails:
                    emails = [email.replace("E-Mail:", "").strip() for email in emails if email]
                    return ",".join(filter(None, emails)).strip()
                else:
                    emails = response.xpath('//*/p[contains(text(),"(at)")]/text()').extract()
                    if emails:
                        emails = [email.strip().replace("(at)", "@").replace(" ", "") for email in emails if email]
                        return ",".join(filter(None, emails)).strip()
            return ""

    def extract_phone(self, response):
        """
        Return phones if possible
        :param self:
        :type self:
        :param response:
        :type response:
        :return:
        :rtype:
        """

        telephones = response.xpath('//*/a[contains(@href,"tel:")]/text()').extract()
        if telephones:
            telephones = [phone.replace("Tel:", "").replace("Phone:", "").replace("Handynummer:", "").strip() for phone
                          in telephones if phone]
            return ",".join(filter(None, telephones)).strip()
        else:
            telephones = response.xpath('//*/p[contains(text(),"nummer")]/text()').extract()
            if telephones:
                telephones = [phone.replace("Tel:", "").replace("Phone:", "").replace("Handynummer:", "").strip() for
                              phone in telephones if (not "Firmanummer" in phone)]
                return ",".join(filter(None, telephones)).strip()
            return ""

    def get_webpage_title(self, response):
        """
        Method tries to find the title of the website
        :param response:
        :type response:
        :return:
        :rtype:
        """
        title = response.xpath('//*/title/text()').extract_first()
        if title:
            return title.strip()
        else:
            title = response.xpath('//*/meta[contains(@name,"title")]/@content').extract_first()
            if title:
                return title.strip()
            else:
                return ""
