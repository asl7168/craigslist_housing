# to avoid issues with the html directory being in the wrong location, please use an absolute filepath
import sys
sys.path.append("/projects/p31502/projects/craigslist")

from time import sleep
from cprint import cprint
from cronable_scraping import do_cron_scrape

locations = ['chicago', 'atlanta', 'boston', 'cleveland', 'denver', 'losangeles', 'memphis', 'seattle', 'sfbay', 'austin', 'dallas', 'detroit', 'houston', 'lasvegas', 'miami', 'minneapolis', 'newyork', 'orangecounty', 'philadelphia', 'phoenix', 'portland', 'raleigh', 'sacramento', 'sandiego', 'washingtondc', 'baltimore', 'bham', 'buffalo', 'charlotte', 'cincinnati', 'columbus', 'hartford', 'indianapolis', 'inlandempire', 'jacksonville', 'kansascity', 'louisville', 'milwaukee', 'muncie', 'nashville', 'newjersey', 'niagara', 'norfolk', 'oklahomacity', 'orlando', 'pittsburgh', 'providence', 'richmond', 'saltlakecity', 'sanantonio', 'sanmarcos', 'stlouis', 'stpetersburg', 'tampa', 'watertown']
with open("/projects/p31502/projects/craigslist/proxies/webshare_proxies.txt") as f: proxies = f.readlines()

def scrape_from(idx: int=0):
	for location in locations[idx:39]:
		try:
			pcpy = proxies.copy()
			do_cron_scrape(city=location, filepath="/projects/p31502/projects/craigslist/html", proxies=pcpy)
		except Exception as e:
			cprint(f"Encountered exception '{e}'\nTrying again in 30 seconds", c="r")
			sleep(30)
			scrape_from(locations.index(location))

scrape_from()