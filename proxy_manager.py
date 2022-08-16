from requests import get
from bs4 import BeautifulSoup
import re
import json 
from tqdm import tqdm
from time import sleep, perf_counter
from cprint import cprint
from webshare_credentials import user, password


def clean_webshare_proxies(proxies_filename: str="./proxies/webshare_proxies.txt") -> list:
    """ Cleans proxies at the given filepath into the standard form x.x.x.x:xxxx; when
    downloading webshare.io proxies, they're of the form x.x.x.x:xxxx:user:password, 
    which is a format that doesn't work with the requests library

    Parameters
    ----------
        proxies_filename (str, optional): filepath to (webshare) proxies. Defaults to
            "./proxies/webshare_proxies.txt"

    Returns
    ----------
        cleaned_proxies (list): list of cleaned proxies (e.g. x.x.x.x:xxxx)
    """
    
    with open(proxies_filename, "r") as proxies_file:
        init_proxies = proxies_file.readlines()

    r = re.compile("[\d\.]+:\d+")  # e.g. 1.2.3.4:5678

    cleaned_proxies = [r.search(proxy)[0] for proxy in init_proxies]  

    bad_starts = ["177.234", "181.177", "185.230", "186.179"]  # some proxies are blocked by quest
    cleaned_proxies = [proxy for proxy in cleaned_proxies if proxy[:7] not in bad_starts]

    with open(proxies_filename, "w") as proxies_file: # overwrite file with cleaned proxies
        [proxies_file.write(proxy + "\n") for proxy in cleaned_proxies]

    return cleaned_proxies


def test_webshare_proxies(proxies_filename: str="./proxies/webshare_proxies.txt", n: int=1):
    """ Tests webshare proxies at the given filepath against a craigslist search link. If 
    an exception occurs, it tries the get request one more time before printing a message
    suggesting removal of the proxy from the proxies file. Additionally, if the proxy is 
    blocked or takes longer than 4 seconds to complete the get request, it suggests removal

    Parameters
    ----------
        proxies_filename (str, optional): filepath to webshare proxies. Defaults to
            "./proxies/webshare_proxies.txt"
        n (int, optional): the number of links to test against
    """

    with open(proxies_filename, "r") as proxies_file:
        proxies = proxies_file.readlines()
    
    base_url = "https://chicago.craigslist.org/d/apartments-housing-for-rent/search/apa?availabilityMode=0&s="
    pbar = tqdm(total=n, desc=f"Testing proxies against {n} craigslist pages")
    for page in range(n):
        url = base_url + str(page * 120)
        
        for proxy in tqdm(proxies, leave=False):  # leave=False so the progress bars stack
            pbar.write(proxy)
            p = {"http": f"http://{user}:{password}@{proxy}", "https": f"http://{user}:{password}@{proxy}"}

            try:
                tic = perf_counter()  # start the timer
                r = get(url, proxies=p)
            except Exception:
                sleep(5)
                try: 
                    tic = perf_counter()  # restart the timer
                    r = get(url, proxies=p)
                except Exception:
                    pbar.write(f"PROXY {proxy[:-1]} IS HAVING AN ISSUE, AND SHOULD BE REMOVED FROM {proxies_filename}\n")
                    continue 
            
            toc = perf_counter()  # stop the timer
            soup = BeautifulSoup(r.text, "html.parser")
            if len(soup.find_all('li', class_= 'result-row')) == 0:
                body = soup.find("body")
                if body and "blocked" in body.text:
                    pbar.write(f"PROXY {proxy[:-1]} IS BLOCKED, AND SHOULD BE REMOVED FROM {proxies_filename}\n")
            elif toc-tic > 4:  # get request took > 4 seconds
                pbar.write(f"PROXY {proxy[:-1]} SEEMS TO BE SLOW, AND SHOULD POTENTIALLY BE REMOVED FROM {proxies_filename}\n")  

            sleep(20/len(proxies))  # standard sleep formula (used in cronable_scraping.py as well)
            
        pbar.update(1)  # increment the page progress bar by 1


if __name__ == "__main__":
    clean_wesbshare_proxies()
