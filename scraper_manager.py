from proxy_manager import clean_webshare_proxies
from GIS_data.state_codes import state_codes


def setup(init: bool=False, filepath: str=None, use_rotating_link: bool=False, webshare_proxies: str=None, for_quest: bool=False):
    """ Creates python files to do an initial scrape of up to 25 pages of posts (3000 posts total) or
    a daily scrape (every post made within 24 hours) for every location in GIS_data/state_codes.py 
    (NOTE: these are not all city names; some are regions).

    Parameters
    ----------
        init (bool, optional): if the python script being created is for an initial scrape or cron scrape.
            Defaults to False
        filepath (str, optional): filepath to the root craigslist directory. Defaults to None
        use_rotating_link (bool, optional): whether or not to use the rotating proxy link (from webshare.io) instead of a proxy 
            list. Defaults to False
        webshare_proxies (str, optional): filepath to webshare_proxies.txt. Defaults to None
        for_quest (bool, optional): whether or not the python script is being run on QUEST (p31502 allocation).
            Defaults to False
    """
    
    init_or_cron = "init" if init else "cron"  
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

    if not filepath:
        if for_quest: filepath = "/projects/p31502/projects/craigslist"
        else: filepath = "."
    else:
        filepath = filepath

    proxy_string = ""
    if not use_rotating_link:
        # make sure proxies are clean
        clean_webshare_proxies() if not webshare_proxies else clean_webshare_proxies(webshare_proxies)
        proxy_string = f"with open(\"{f'{filepath}/proxies/webshare_proxies.txt' if not webshare_proxies else webshare_proxies}\") " \
             "as f: proxies = f.readlines()\n\n"
    output = ""
    output += f"# to avoid issues with the html directory being in the wrong location, please use an absolute filepath\n" \
              f"import sys\nsys.path.append(\"{filepath}/\")\n\n" \
              "from time import sleep\n" \
              "from cprint import cprint\n" \
              f"from cronable_scraping import CraigslistScraper\n\n" \
              f"locations = {locations}\n" \
              f"{proxy_string}" \
              "def scrape_from(idx: int=0):\n" \
              "\tfor location in locations[idx:]:\n"
    output += "\t\tpcpy = proxies.copy()\n" if not use_rotating_link else ""
    # don't actually want to use do_cron_scrape now that we use selenium -- need access to driver in event of error so we can quit it
    # otherwise, if there are multiple errors (which cause reruns), instances of firefox can build up and cause issues
    output += f"\t\tscraper = CraigslistScraper(city=location, filepath=\"{filepath}/html\", "
    output += f"scrape_by_date=False, " if init else ""
    output += f"proxies=pcpy" if not use_rotating_link else f"use_rotating_link=True"
    output += ")\n" \
              "\t\ttry:\n" \
              "\t\t\tscraper.scrape()\n"\
              "\t\texcept Exception as e:\n" \
              "\t\t\ttry:\n\t\t\t\tcprint(f\"Encountered exception \'{e}\'\\nTrying again in 30 seconds\", c=\"r\")\n" \
              "\t\t\texcept Exception:\n\t\t\t\tcprint(\"Encountered an unprintable exception. Trying again in 30 seconds\", c=\"r\")\n" \
              "\t\t\tscraper.driver.quit()\n" \
              "\t\t\tsleep(30)\n" \
              "\t\t\tscrape_from(locations.index(location))\n\n" \
              "scrape_from()\n"
             
    with open(f"scripts/{init_or_cron}_scrape.py", "w") as script:
        script.write(output)
