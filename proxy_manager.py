from requests import get
from bs4 import BeautifulSoup
import re
import json 


def verify_proxy(proxy: str) -> bool:
    try:
        craigslist_test = get(
            "https://chicago.craigslist.org/d/apartments-housing-for-rent/search/apa?availabilityMode=0&s=", 
            proxies={
                "http": proxy, 
                "https": proxy
                },
            timeout=4
        )

        print(f"{proxy} WORKED")
        return craigslist_test.ok
    except:
        print(f"{proxy} FAILED")
        return False

def get_sslproxies() -> set:
    r = get("https://sslproxies.org/")
    html_soup = BeautifulSoup(r.text, "html.parser")
    table = html_soup.find("table", class_="table table-striped table-bordered")
    rows = table.find_all("tr")[1:]
    ips_and_ports = [row.find_all("td")[:2] for row in rows]
    
    proxies = {iap[0].text + ":" + iap[1].text for iap in ips_and_ports}
    print(f"--------------------\nVERIFYING {len(proxies)} PROXIES FROM 'https://sslproxies.org/'")

    verified_proxies = {p for p in proxies if verify_proxy(p)}
    print(f"VERIFIED {len(verified_proxies)}/{len(proxies)} PROXIES FROM 'https://sslproxies.org/'\n--------------------\n")
    return verified_proxies


def get_spysone() -> set:
    with open("proxies/Free proxy list, public proxy servers list online, live proxies.html", "r") as html_file:
        html_soup = BeautifulSoup(html_file.read(), "html.parser")
        proxy_cells = [p.text for p in html_soup.find_all("font", class_="spy14")]
        r = re.compile("(\d+(\.|\:))+\d+")

        proxies = set(filter(r.match, proxy_cells))
        print(f"--------------------\nVERIFYING {len(proxies)} PROXIES FROM 'https://spys.one/free-proxy-list/US/'")

        verified_proxies = {p for p in proxies if verify_proxy(p)}
        print(f"VERIFIED {len(verified_proxies)}/{len(proxies)} PROXIES FROM 'https://spys.one/free-proxy-list/US/'\n--------------------\n")
        return verified_proxies


def get_apiproxy() -> set:
    html_files = ["proxies/Free Proxy API Access.html", "proxies/Free Proxy API Access (2).html"]
    proxies = {}

    for hf in html_files:
        with open(hf, "r") as html_file:
            html_soup = BeautifulSoup(html_file.read(), "html.parser")
            rows = {row.find_all("td")[:2] for row in html_soup.find("tbody").find_all("tr")}
            rows = {{cell.text.strip() for cell in row} for row in rows}
            page_proxies = {":".join(row) for row in rows}
            proxies += page_proxies

    print(f"--------------------\nVERIFYING {len(proxies)} PROXIES FROM 'https://apiproxyfree.com/'")

    verified_proxies = {p for p in proxies if verify_proxy(p)}
    print(f"VERIFIED {len(verified_proxies)}/{len(proxies)} PROXIES FROM 'https://apiproxyfree.com/'\n--------------------\n")
    return verified_proxies


def get_proxies(proxies_outfilename: str = "proxies/verified_proxies.json") -> list:
    sslproxies = get_sslproxies()
    spysoneproxies = get_spysone()
    apiproxyproxies = get_apiproxy()

    proxies = list(sslproxies | spysoneproxies | apiproxyproxies)
    print(f"\n--------------------\nVERIFIED {len(proxies)} PROXIES TOTAL")
    
    json_obj = json.dumps(proxies, indent=1)
    with open(proxies_outfilename, "w") as outfile:
        outfile.write(json_obj)

    return proxies


def reverify_proxies(proxies_filename: str = "proxies/verified_proxies.json", rever_filename: str = "proxies/reverified_proxies.json") -> list: 
    with open(proxies_filename, "r") as proxies_file: 
        proxies = json.load(proxies_file)

    reverified_proxies = list({proxy for proxy in proxies if verify_proxy(proxy)})
    json_obj = json.dumps(reverified_proxies, indent=1)
    with open(rever_filename, "w") as outfile:
        outfile.write(json_obj)  

    return reverified_proxies
    
if __name__ == "main":
    get_proxies()
    reverify_proxies()
