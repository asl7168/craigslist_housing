# to avoid issues with the html directory being in the wrong location, please use an absolute filepath
import sys
sys.path.append("/projects/p31502/projects/craigslist/")

from time import sleep
from cprint import cprint
from cronable_scraping import CraigslistScraper

locations = ['chicago', 'atlanta', 'boston', 'cleveland', 'denver', 'losangeles', 'memphis', 'seattle', 'sfbay', 'austin', 'dallas', 'detroit', 'houston', 'lasvegas', 'miami', 'minneapolis', 'newyork', 'orangecounty', 'philadelphia', 'phoenix', 'portland', 'raleigh', 'sacramento', 'sandiego', 'washingtondc', 'baltimore', 'bham', 'buffalo', 'charlotte', 'cincinnati', 'columbus', 'hartford', 'indianapolis', 'inlandempire', 'jacksonville', 'kansascity', 'louisville', 'milwaukee', 'muncie', 'nashville', 'newjersey', 'norfolk', 'oklahomacity', 'orlando', 'pittsburgh', 'providence', 'richmond', 'saltlakecity', 'sanantonio', 'sanmarcos', 'stlouis', 'tampa']
with open("/projects/p31502/projects/craigslist/proxies/webshare_proxies.txt") as f: proxies = f.readlines()

def scrape_from(idx: int=0):
	for location in locations[idx:]:
		pcpy = proxies.copy()
		scraper = CraigslistScraper(city=location, filepath="/projects/p31502/projects/craigslist/html", scrape_by_date=False, proxies=pcpy)
		try:
			scraper.scrape()
		except Exception as e:
			try:
				cprint(f"Encountered exception '{e}'\nTrying again in 30 seconds", c="r")
			except Exception:
				cprint("Encountered an unprintable exception. Trying again in 30 seconds", c="r")
			scraper.driver.quit()
			sleep(30)
			scrape_from(locations.index(location))

scrape_from()
