import scrapy
from AutoScrapy.items import BevhItem
from scrapy.http import HtmlResponse
import urllib.parse
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9,pl-PL;q=0.8,pl;q=0.7,nl-NL;q=0.6,nl;q=0.5',
    'content-type': 'application/json',
}


class Bevh(scrapy.Spider):
    """
    Spider to get the data from the Bevh
    """
    name = "Bevh"

    custom_settings = {
        # 'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': 'True',
        'FEED_URI': 'Bevh.csv',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
    }
    start_urls = ["https://www.bevh.org/mitglieder/bevh-mitglieder/"]

    def parse(self, response):
        """
        Method looks for the shop links

        :param response: the fully downloaded webpage
        :return: the iterator over the categories links
        """
        list_of_companies = response.xpath('//*/div[@class="inner-wrap gradient-green"]')
        for company in list_of_companies:
            item = BevhItem()
            name = company.xpath('.//p/text()').extract_first()
            url = company.xpath('.//a/@href').extract_first()

            # assign to the item
            if name:
                item['company_name'] = name
            if url:
                item['url'] = url
                yield scrapy.Request(url, callback=self.parse_webpage, meta={'item': item})
            else:
                yield item

        next_page = response.xpath('//*/a[@rel="next"]/@href').extract_first()
        if next_page:
            next_page = "https://www.bevh.org/" + next_page
            print("Following next page was found: {}", next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_webpage(self, response):
        """
        parse webpage, needs to be smarter
        :param item:
        :type item:
        :param response:
        :type response:
        :return:
        :rtype:
        """
        item = response.meta['item']
        print("Request url {}, actual requested url {}".format(item['url'], response.request.url))
        # website url
        item['website_url'] = response.request.url

        item['name'] = self.guess_company_name(response)
        item['domain'] = self.get_domain(response)

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

    def guess_company_name(self, response):
        """
        Guess the name of the company
        :param response:
        :type response:
        :return:
        :rtype:
        """
        # TODO here guess the name of the company
        # if og:title or title or smth else
        # if domain in the title then its the name
        # if not
        # take domain

        parts = urllib.parse.urlparse(response.url)
        name_parts = parts.netloc.split(".")
        if len(name_parts) > 2:
            name = name_parts[1]
        else:
            name = name_parts[0]

        site_name = response.xpath('//*/meta[@property="description"]/@content').extract_first()
        if site_name:
            return site_name
        else:
            return name.title()

    def get_domain(self, response):
        """
        Get domain name of the webpage
        :param response:
        :type response:
        :return:
        :rtype:
        """
        parts = urllib.parse.urlparse(response.url)
        domain = parts.netloc
        return domain
