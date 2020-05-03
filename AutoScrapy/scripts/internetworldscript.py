import csv
from html.parser import HTMLParser
import requests
import json
import pprint

pages = 49
results_per_page = 34

tags_dict = {}


class MLStripper(HTMLParser):
	def __init__(self):
		super().__init__()
		self.reset()
		self.fed = []
		self.convert_charrefs = True

	def handle_data(self, d):
		self.fed.append(d)

	def get_data(self):
		return ''.join(self.fed)


def strip_tags(html):
	s = MLStripper()
	s.feed(html)
	return s.get_data()


class InternetWorldItem(object):
	"""
	Class to hold results of the queries
	"""

	def __init__(self):
		self.name = ""
		self.street = ""
		self.zip_code = ""
		self.city = ""
		self.country = ""
		self.phone = ""
		self.fax = ""
		self.user = ""
		self.desc = ""
		self.url = ""
		self.website = ""
		self.email = ""
		self.twitter = ""
		self.facebook = ""
		self.linkedin = ""
		self.industries = []


url_base = "https://dienstleister.internetworld.de/api/exhibitor/?page="

headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
	'Accept-Language': 'en-US,en;q=0.9,pl-PL;q=0.8,pl;q=0.7,nl-NL;q=0.6,nl;q=0.5',
	'content-type': 'application/json',
	'origin': 'https://dienstleister.internetworld.de/'}


def process_response(response):
	"""
	Method processes the json loaded from the response into the item
	:param response:
	:return:
	"""
	for company in response:
		item = InternetWorldItem()
		if 'company' in company['company_info']:
			item.name = company['company_info']['company']
		if 'about_us' in company['company_info']:
			item.desc = strip_tags(company['company_info']['about_us'])
		if 'email' in company['company_info']:
			item.email = company['company_info']['email']
		if 'street' in company['company_info']:
			item.street = company['company_info']['street']
		if 'plz' in company['company_info']:
			item.zip_code = company['company_info']['plz']
		if 'city' in company['company_info']:
			item.city = company['company_info']['city']
		if 'country' in company['company_info']:
			item.country = company['company_info']['country']
		if 'phone' in company['company_info']:
			item.phone = company['company_info']['phone']
		if 'fax' in company['company_info']:
			item.fax = company['company_info']['fax']
		if 'firstname' and 'lastname' in company['user_info']:
			item.user = company['user_info']['firstname'] + " " + company['user_info']['lastname']
		item.url = 'https://dienstleister.internetworld.de/firma/' + str(company['ID'])

		for link in company['company_links']:
			if link['slug'] == "facebook":
				item.facebook = link['url']
			if link['slug'] == "linkedin":
				item.linkedin = link['url']
			if link['slug'] == "twitter":
				item.twitter = link['url']
			if link['slug'] == "website":
				item.website = link['url']

		for value in company['company_tags']:
			item.industries.append(get_tag_by_id(value))

		write_to_file(item)


def process_tags(response):
	"""
	Method processes the categories into the dict
	:param response:
	:return:
	"""
	for tag in response:
		id = tag['id']
		name = tag['slug']
		tags_dict[id] = name
	print(tags_dict)


def get_tag_by_id(id):
	"""
	Method returns the tag by the id passed
	:param id: of tag
	:return:
	"""
	return tags_dict.get(id, "")


def write_to_file(item):
	"""
	Methods writes completed object to the file
	:param item:
	:return:
	"""
	headers = ['name', 'desc', 'email', 'street', 'zip-code', 'city', 'country', 'phone', 'fax', 'user', 'url',
			   'facebook', 'linkedin', 'twitter', 'website', 'industries']
	dict_to_print = {'name': item.name,
					 'desc': item.desc,
					 'email': item.email,
					 'street': item.street,
					 'zip-code': item.zip_code,
					 'city': item.city,
					 'country': item.country,
					 'phone': item.phone,
					 'fax': item.fax,
					 'user': item.user,
					 'url': item.url,
					 'facebook': item.facebook,
					 'linkedin': item.linkedin,
					 'twitter': item.twitter,
					 'website': item.website,
					 'industries': str(item.industries).strip('[').strip(']').replace('\'', '')
					 }

	with open("results.csv", 'a', encoding='utf-8', newline='') as file:
		writer = csv.DictWriter(file, delimiter='\t', fieldnames=headers)
		writer.writerow(dict_to_print)
		print(dict_to_print)


if __name__ == "__main__":
	# write headers
	with open('results.csv', 'w', newline='') as outcsv:
		writer = csv.writer(outcsv, delimiter='\t')
		writer.writerow(["name", "desc", "email", "street", "zip-code", "city", "country", "phone", "faxe",
						 "user", "url", "facebook", "linkedin", "twitter", "website", "tags"])

		# get categories to the dictionary
		url = 'https://dienstleister.internetworld.de/api/tag/'
		r = requests.get(url, headers=headers)
		response = json.loads(r.text)
		process_tags(response)

	for page in range(50):
		url = url_base + str(page)
		r = requests.get(url, headers=headers)
		response = json.loads(r.text)
		process_response(response)
