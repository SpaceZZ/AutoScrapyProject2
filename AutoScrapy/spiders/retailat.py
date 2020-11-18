import scrapy
from AutoScrapy.items import RetialAtItem
from scrapy.http import HtmlResponse
import urllib.parse
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9,pl-PL;q=0.8,pl;q=0.7,nl-NL;q=0.6,nl;q=0.5',
    'content-type': 'application/json',
}


class RetailAt(scrapy.Spider):
    """
    Spider to get the data from the eurocis
    """
    name = "RetailAtSpider"

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': 'False',
        'FEED_URI': 'RetailAt.csv',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
    }
    # allowed_domains = ['retail.at']
    start_urls = ["https://retail.at/oesterreichische-webshops/"]

    def parse(self, response):
        """
        Method looks for the indexes

        :param response: the fully downloaded webpage
        :return: the iterator over the categories links
        """
        list_of_categories_selector = response.xpath('.//*/h4/a')
        for link_selector in list_of_categories_selector:
            category = link_selector.xpath('./text()').extract_first()
            redirect_url = link_selector.xpath('./@href').extract_first()
            yield scrapy.Request(url=redirect_url, callback=self.parse_data, meta={'category': category})

    def parse_data(self, response):
        """
        Method parses the data for each individual link
        :param response:
        :return:
        """
        category = response.meta['category']

        shop_selector = response.xpath('.//*/div[@class="entry-content"]/ul/li')
        for shop in shop_selector:
            item = RetialAtItem()
            item['category'] = category
            # shop name
            item['name'] = shop.xpath('./a/text()').extract_first().strip()
            # get category url
            item['category_url'] = response.request.url
            # website
            item['url'] = shop.xpath('./a/@href').extract_first()
            url = item['url']
            # description of the shop
            list_description = shop.xpath('./text()').extract()
            if list_description:
                # clean the description
                description = "".join(list_description).strip()
                new_description = description.replace("– ", "").replace(":- )", "")
                item['description'] = new_description

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
        # get description from website
        desc = response.xpath('//*/meta[@itemprop="description"]/@content').extract_first()
        desc1 = response.xpath('//*/meta[@name="description"]/@content').extract_first()

        desc_length = 50

        if desc1:
            item['website_desc'] = desc1[:desc_length].strip()
        else:
            if desc:
                item['website_desc'] = desc[:desc_length].strip()
            else:
                desc = response.xpath('//*/meta[@property="description"]/@content').extract_first()
                if desc:
                    item['website_desc'] = desc[:desc_length].strip()

        # get keywords from website
        tags = response.xpath('//*/meta[@property="keywords"]/@content').extract_first()
        tags1 = response.xpath('//*/meta[@name="keywords"]/@content').extract_first()
        if tags:
            item['keywords'] = tags.strip()
        elif tags1:
            item['keywords'] = tags1.strip()
        else:
            tags = response.xpath('//*/meta[@itemprop="keywords"]/@content').extract_first()
            if tags:
                item['keywords'] = tags.strip()

        # try to get email and phones
        item['email'] = self.extract_email(response)
        item['phone'] = self.extract_phone(response)

        if not item['email']:
            # try to get contact info
            # check if there is kontakt link on the page
            item = self.check_webpage_for_contact_details(item, response, "Impressum")

            if not item['email']:
                try:
                    # try Contact
                    item = self.check_webpage_for_contact_details(item, response, "Kontakt")

                except Exception as e:
                    print("Exception", e)

        item['country'] = "Oestreich"
        if item['email']:
            item['email'] = item['email'].replace("(at)", "@")
        yield item

    def check_webpage_for_contact_details(self, item, response, suffix):
        """
        Check if there is specifc keyword link in the webpage
        :param item:
        :type item:
        :param response:
        :type response:
        :param suffix:
        :type suffix:
        :return:
        :rtype:
        """
        check_contact = response.xpath('//*/a[contains(text(),{})]/@href'.format("\"" + suffix + "\"")).extract_first()
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

    def try_contact_page(self, response, suffix):
        resp = requests.get(response.request.url + suffix)
        return resp

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
            return ",".join(emails).strip()
        else:
            emails = response.xpath('//*/a[contains(@href,"mailto:")]/@href').extract()
            if emails:
                emails = [email.strip().replace("mailto:", "") for email in emails if email]
                return ",".join(emails).strip()
            else:
                emails = response.xpath('//*/p[contains(text(),"E-Mail:")]/text()').extract()
                if emails:
                    emails = [email.strip() for email in emails if email]
                    return ",".join(emails).strip()
                else:
                    emails = response.xpath('//*/p[contains(text(),"(at)")]/text()').extract()
                    if emails:
                        emails = [email.strip().replace("(at)", "@").replace(" ", "") for email in emails if email]
                        return ",".join(emails).strip()
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
            return ",".join(telephones).strip()
        else:
            telephones = response.xpath('//*/p[contains(text(),"nummer")]/text()').extract()
            if telephones:
                telephones = [phone.replace("Tel:", "").replace("Phone:", "").replace("Handynummer:", "").strip() for
                              phone in telephones if phone]
                return ",".join(telephones).strip()
            return ""
