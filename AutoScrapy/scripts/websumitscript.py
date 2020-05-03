import csv

import requests
import json
import pprint

pages = 7
results_per_page = 34

class WebsummitItem(object):
	"""
	Class to hold results of the queries
	"""
	def __init__(self):
		self.name = ""
		self.city = ""
		self.desc = ""
		self.website = ""
		self.instagram = ""
		self.twitter = ""
		self.facebook = ""
		self.linkedin = ""
		self.country = ""
		self.industries = []


url = 'https://x0o1h31a99-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.33.0)%3B%20Browser%20(lite)%3B%20react%20(16.12.0)%3B%20react-instantsearch%20(5.7.0)%3B%20JS%20Helper%20(2.28.0)&x-algolia-application-id=X0O1H31A99'
payload = {"requests":[{"indexName":"Avenger_Company_production_ws19",
						"params":"query=&hitsPerPage=34&maxValuesPerFacet=10&page=2&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22tracks.ws19%22%5D&tagFilters=&facetFilters=%5B%5B%22tracks.ws19%3AExhibitor%22%5D%5D"}],
		   			 "apiKey":"YmM4YzVlODMzODExMDg4ZmMxOThjYTQ4ODg5YTBlNmY4NTY3MjJkNGNkNzBiODg3MGMxYjI4NDNjNjllYzA4YWZpbHRlcnM9X3RhZ3MlM0F3czE5JnJlc3RyaWN0SW5kaWNlcz0lNUIlMjJBdmVuZ2VyX0NvbXBhbnlfcHJvZHVjdGlvbiUyMiUyQyUyMkF2ZW5nZXJfQ29tcGFueV9wcm9kdWN0aW9uLnRtcCUyMiUyQyUyMkF2ZW5nZXJfQ29tcGFueV9wcm9kdWN0aW9uX3dzMTklMjIlMkMlMjJBdmVuZ2VyX0FwcGVhcmFuY2VfcHJvZHVjdGlvbiUyMiUyQyUyMkF2ZW5nZXJfQXBwZWFyYW5jZV9wcm9kdWN0aW9uLnRtcCUyMiUyQyUyMkF2ZW5nZXJfQXBwZWFyYW5jZV9wcm9kdWN0aW9uX3dzMTklMjIlMkMlMjJBdmVuZ2VyX0F0dGVuZGFuY2VfcHJvZHVjdGlvbiUyMiUyQyUyMkF2ZW5nZXJfQXR0ZW5kYW5jZV9wcm9kdWN0aW9uLnRtcCUyMiUyQyUyMkF2ZW5nZXJfQXR0ZW5kYW5jZV9wcm9kdWN0aW9uX3dzMTklMjIlNUQ"}

headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
			'Accept-Language': 'en-US,en;q=0.9,pl-PL;q=0.8,pl;q=0.7,nl-NL;q=0.6,nl;q=0.5',
			'content-type': 'application/json',
			'origin' : 'https://websummit.com'}


def process_response(response):
	"""
	Method processes the json loaded from the response into the item
	:param response:
	:return:
	"""
	for company in response['results'][0]['hits']:
		item = WebsummitItem()
		item.name = company['name']
		item.desc = company['elevator_pitch']
		item.city = company['city']
		item.country = company['country']
		item.website = company['external_urls']['homepage']
		item.instagram = company['external_urls']['instagram']
		item.twitter = company['external_urls']['twitter']
		item.facebook = company['external_urls']['facebook']
		item.linkedin = company['external_urls']['linkedin']
		industries = company['industries']
		for key, value in industries.items():
			if value:
				if value not in item.industries:
					item.industries.append(value)
		write_to_file(item)

def write_to_file(item):
	"""
	Methods writes completed object to the file
	:param item:
	:return:
	"""
	headers = ['name', 'city', 'country', 'industries', 'desc', 'website', 'instagram', 'twitter', 'facebook', 'linkedin']
	dict_to_print = {'name' : item.name,
					 'city' : item.city,
					 'country' : item.country,
					 'industries' : str(item.industries).strip('[').strip(']').replace('\'',''),
					 'desc' : item.desc,
					 'website' : item.website,
					 'instagram' : item.instagram,
					 'twitter' : item.twitter,
					 'facebook' : item.facebook,
					 'linkedin' : item.linkedin}

	with open("results.csv", 'a', encoding='utf-8', newline='') as file:
		writer = csv.DictWriter(file, delimiter='\t', fieldnames=headers)
		writer.writerow(dict_to_print)
		print(dict_to_print)


with open('results.csv', 'w', newline='') as outcsv:
    writer = csv.writer(outcsv, delimiter ='\t')
    writer.writerow(["Name", "City", "Country", "Industries", "Desc", "Website", "Instagram", "Twitter", "Facebook", "LinkedIn"])


# for page in range(8):
# 	payload = {"requests":[{"indexName":"Avenger_Company_production_ws19",
# 						"params":"query=&hitsPerPage=34&maxValuesPerFacet=10&page="+str(page)+"&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22tracks.ws19%22%5D&tagFilters=&facetFilters=%5B%5B%22tracks.ws19%3AExhibitor%22%5D%5D"}],
# 		   			 "apiKey":"YmM4YzVlODMzODExMDg4ZmMxOThjYTQ4ODg5YTBlNmY4NTY3MjJkNGNkNzBiODg3MGMxYjI4NDNjNjllYzA4YWZpbHRlcnM9X3RhZ3MlM0F3czE5JnJlc3RyaWN0SW5kaWNlcz0lNUIlMjJBdmVuZ2VyX0NvbXBhbnlfcHJvZHVjdGlvbiUyMiUyQyUyMkF2ZW5nZXJfQ29tcGFueV9wcm9kdWN0aW9uLnRtcCUyMiUyQyUyMkF2ZW5nZXJfQ29tcGFueV9wcm9kdWN0aW9uX3dzMTklMjIlMkMlMjJBdmVuZ2VyX0FwcGVhcmFuY2VfcHJvZHVjdGlvbiUyMiUyQyUyMkF2ZW5nZXJfQXBwZWFyYW5jZV9wcm9kdWN0aW9uLnRtcCUyMiUyQyUyMkF2ZW5nZXJfQXBwZWFyYW5jZV9wcm9kdWN0aW9uX3dzMTklMjIlMkMlMjJBdmVuZ2VyX0F0dGVuZGFuY2VfcHJvZHVjdGlvbiUyMiUyQyUyMkF2ZW5nZXJfQXR0ZW5kYW5jZV9wcm9kdWN0aW9uLnRtcCUyMiUyQyUyMkF2ZW5nZXJfQXR0ZW5kYW5jZV9wcm9kdWN0aW9uX3dzMTklMjIlNUQ"}
# 	r = requests.post(url, data=json.dumps(payload), headers=headers)
# 	response = json.loads(r.text)
# 	process_response(response)

for page in range(60):
	payload = {"requests": [{"indexName": "Avenger_Company_production_ws19",
							 "params": "query=&hitsPerPage=40&maxValuesPerFacet=10&page=" + str(page) + "&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22tracks.ws19%22%5D&tagFilters=&facetFilters=%5B%5B%22tracks.ws19%3AGROWTH%22%2C%22tracks.ws19%3ABETA%22%2C%22tracks.ws19%3AALPHA%22%5D%5D"}],
			   "apiKey": "YmM4YzVlODMzODExMDg4ZmMxOThjYTQ4ODg5YTBlNmY4NTY3MjJkNGNkNzBiODg3MGMxYjI4NDNjNjllYzA4YWZpbHRlcnM9X3RhZ3MlM0F3czE5JnJlc3RyaWN0SW5kaWNlcz0lNUIlMjJBdmVuZ2VyX0NvbXBhbnlfcHJvZHVjdGlvbiUyMiUyQyUyMkF2ZW5nZXJfQ29tcGFueV9wcm9kdWN0aW9uLnRtcCUyMiUyQyUyMkF2ZW5nZXJfQ29tcGFueV9wcm9kdWN0aW9uX3dzMTklMjIlMkMlMjJBdmVuZ2VyX0FwcGVhcmFuY2VfcHJvZHVjdGlvbiUyMiUyQyUyMkF2ZW5nZXJfQXBwZWFyYW5jZV9wcm9kdWN0aW9uLnRtcCUyMiUyQyUyMkF2ZW5nZXJfQXBwZWFyYW5jZV9wcm9kdWN0aW9uX3dzMTklMjIlMkMlMjJBdmVuZ2VyX0F0dGVuZGFuY2VfcHJvZHVjdGlvbiUyMiUyQyUyMkF2ZW5nZXJfQXR0ZW5kYW5jZV9wcm9kdWN0aW9uLnRtcCUyMiUyQyUyMkF2ZW5nZXJfQXR0ZW5kYW5jZV9wcm9kdWN0aW9uX3dzMTklMjIlNUQ"}
	r = requests.post(url, data=json.dumps(payload), headers=headers)
	response = json.loads(r.text)
	process_response(response)