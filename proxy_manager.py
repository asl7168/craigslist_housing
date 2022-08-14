from requests import get
from bs4 import BeautifulSoup
import re
import json 
from tqdm import tqdm
from time import sleep, perf_counter
from cprint import cprint
from webshare_credentials import user, password


def clean_webshare_proxies(proxies_filename: str = "proxies/webshare_proxies.txt") -> list:
    with open(proxies_filename, "r") as proxies_file:
        init_proxies = proxies_file.readlines()

    r = re.compile("[\d\.]+:\d+")

    cleaned_proxies = [r.search(proxy)[0] for proxy in init_proxies]

    bad_starts = ["177.234", "181.177", "185.230", "186.179"]  # some proxies are blocked by quest
    cleaned_proxies = [proxy for proxy in cleaned_proxies if proxy[:7] not in bad_starts]

    with open(proxies_filename, "w") as proxies_file:
        [proxies_file.write(proxy + "\n") for proxy in cleaned_proxies]

    return cleaned_proxies


def test_webshare_proxies(proxies_filename: str = "proxies/webshare_proxies.txt", n: int=5):
    with open(proxies_filename, "r") as proxies_file:
        proxies = proxies_file.readlines()
    
    base_url = "https://chicago.craigslist.org/d/apartments-housing-for-rent/search/apa?availabilityMode=0&s="
    pbar = tqdm(total=n, desc=f"Testing proxies against {n} craigslist pages")
    for page in range(n):
        url = base_url + str(page * 120)
        
        for proxy in tqdm(proxies, leave=False):
            pbar.write(proxy)
            p = {"http": f"http://{user}:{password}@{proxy}", "https": f"http://{user}:{password}@{proxy}"}

            try:
                tic = perf_counter()
                r = get(url, proxies=p)
            except Exception:
                sleep(5)
                try: 
                    tic = perf_counter()
                    r = get(url, proxies=p)
                except Exception:
                    pbar.write(f"PROXY {proxy[:-1]} IS HAVING AN ISSUE, AND SHOULD BE REMOVED FROM {proxies_filename}\n")
                    continue 
            
            toc = perf_counter()
            soup = BeautifulSoup(r.text, "html.parser")
            if len(soup.find_all('li', class_= 'result-row')) == 0:
                body = soup.find("body")
                if body and "blocked" in body.text:
                    pbar.write(f"PROXY {proxy[:-1]} IS BLOCKED, AND SHOULD BE REMOVED FROM {proxies_filename}\n")
            elif toc-tic > 4:  # proxy took > 4 seconds to get
                pbar.write(f"PROXY {proxy[:-1]} SEEMS TO BE SLOW, AND SHOULD POTENTIALLY BE REMOVED FROM {proxies_filename}\n")  

            sleep(20/len(proxies))
            
        pbar.update(1)


if __name__ == "__main__":
    clean_wesbshare_proxies()
