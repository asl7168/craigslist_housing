from proxy_manager import clean_wesbshare_proxies
from state_codes import state_codes
import os
from math import floor, ceil
import json


def setup(init: bool=False):
    init_or_cron = "init" if init else "cron"
    initcron_dir = f"./scripts/{init_or_cron}_scrapers"
    if not os.path.exists(initcron_dir): os.mkdir(initcron_dir)
        
    proxies = clean_wesbshare_proxies()  # reverify proxies, then store them here
    locations = ["chicago", "atlanta", "boston", "cleveland", "denver", "losangeles", "memphis", "seattle", 
                "sfbay", "austin", "dallas", "detroit", "houston", "lasvegas", "miami", "minneapolis", 
                "newyork", "orangecounty", "philadelphia", "phoenix", "portland", "raleigh", "sacramento", 
                "sandiego", "washingtondc"]  # ordered by priority

    [locations.append(l) for l in list(state_codes.keys()) if l not in locations]  # add non-priority locations
    
    # instead of giving one proxy to each location, give all proxies to every location and run them in sequence
    # e.g. if we have 20 proxies, instead of making 20 scripts to run concurrently, just make the wait time
    # equal to 1 second and make that the frequency we rotate proxies at (see cronable_scraping.py); now, the
    # estimated time to do one initial scrape (assuming 3000 posts) is = 16hrs/20proxies = 0.8hrs = 48min.
    # we can't do an initial scrape on QUEST anyways, so also just store them all concurrently in one file --
    # though, even if we could, at 48 min for ~55 locations, that's only 44 hrs of total run time, which is a 
    # quarter of QUEST's 168 hr max jobtime

    output = f"# please run this file from the root directory, not {initcron_dir[2:]}\n" \
             "import sys\nsys.path.append('./')\n\n" \
             "from time import sleep\n" \
             "from cprint import cprint\n" \
             f"from cronable_scraping import do_{init_or_cron}_scrape\n\n" \
             f"locations = {locations}\n" \
             f"proxies = {proxies}\n\n" \
             "def scrape_from(idx: int=0):\n" \
             "\tfor location in locations[idx:]:\n" \
             "\t\ttry:\n"  \
             "\t\t\tpcpy = proxies.copy()\n"  \
             f"\t\t\tdo_{init_or_cron}_scrape(city=location, filepath=\"./html\", proxies=pcpy)\n" \
             "\t\texcept Exception as e:\n" \
             "\t\t\tcprint(f'Encountered exception \"{e}\"\\nTrying again in 30 seconds', c=\"r\")\n" \
             "\t\t\tsleep(30)\n" \
             "\t\t\tscrape_from(locations.index(location))\n\n" \
             "scrape_from()"
             

    with open(f"{initcron_dir}/{init_or_cron}_scrape.py", "w") as script:
        script.write(output)
