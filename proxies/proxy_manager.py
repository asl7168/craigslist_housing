from requests import get
from bs4 import BeautifulSoup
import re

def test_proxy(proxy):
    try:
        craigslist_test = get(
            "https://chicago.craigslist.org/d/apartments-housing-for-rent/search/apa?availabilityMode=0&s=", 
            proxies={
                "http": proxy, 
                "https": proxy
                },
            timeout=2
        )

        print(f"{proxy} WORKED")
        return craigslist_test.ok
    except:
        print(f"{proxy} FAILED")
        return False

def get_sslproxies():
    r = get("https://sslproxies.org/")
    html_soup = BeautifulSoup(r.text, "html.parser")
    table = html_soup.find("table", class_="table table-striped table-bordered")
    rows = table.find_all("tr")[1:]
    ips_and_ports = [row.find_all("td")[:2] for row in rows]
    proxies = [iap[0].text + ":" + iap[1].text for iap in ips_and_ports]

    working_proxies = [p for p in proxies if test_proxy(p)]
    return working_proxies


def get_spysone():
    with open("Free proxy list, public proxy servers list online, live proxies.html", "r") as html_file:
        html_soup = BeautifulSoup(html_file.read(), "html.parser")
        proxy_cells = [p.text for p in html_soup.find_all("font", class_="spy14")]
        r = re.compile("(\d+(\.|\:))+\d+")
        proxies = list(filter(r.match, proxy_cells))
        working_proxies = [p for p in proxies if test_proxy(p)]       
        return working_proxies


def assemble():
    sslproxies = get_sslproxies()
    spysone = get_spysone()
