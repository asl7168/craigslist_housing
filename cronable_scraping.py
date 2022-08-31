# -*- coding: utf-8 -*-
"""
Created on Tue   Jun 01   2021
Updated          Jun-August 2022

@author: lmcox, asl7168

This script retrieves HTML pages for housing listings on Cragislist.

Some code and tips taken from: https://towardsdatascience.com/web-scraping-craigslist-a-complete-tutorial-c41cea4f4981
"""
#%%
import os, sys
if os.path.exists("/projects/p31502/projects/craigslist"): sys.path.append("projects/p31502/projects/craigslist")

from requests import get
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from datetime import date
import time
from bs4 import BeautifulSoup
from tqdm import tqdm
from math import ceil
from webshare_credentials import user, password
from cprint import cprint


# note: any instance of the number 120 is due to craigslist returning 120 results per page
class CraigslistScraper:
    def __init__(self, city: str, filepath: str=None, scrape_by_date: bool=True, number_of_pages: int=25, 
                 use_rotating_link: bool=False, proxies: list=None):
        """ Creates a craigslist scraper for a specific city, and specifies whether it should scrape by posts made today, how
        many pages should be scraped if not, and a list of proxies to scrape using

        Parameters
        ----------
            city (str): the name of the city to scrape for (NOTE: confirm {city}.craigslist.org exists; it might named differently)
            filepath (str, optional): the filepath to the html directory. Defaults to None
            scrape_by_date (bool, optional): whether or not to scrape by posts made today. Defaults to True
            number_of_pages (int, optional): the number of pages to scrape (for an init scrape). Defaults to 25 for 3000 posts (NOTE:
                the frontend update seems to set the cap to 10000, so this may need to change to 84 in the future for init scrapes)
            use_rotating_link (bool, optional): whether or not to use the rotating proxy link (from webshare.io) instead of a proxy 
                list. Defaults to False
            proxies (list, optional): a list of proxies to scrape using. Defaults to None
        """
        
        self.city = city
        self.filepath = filepath + "/" + city if filepath else f"./html/{city}"  # where html files for the city should be saved
        if not os.path.exists(self.filepath): os.makedirs(self.filepath)
        
        self.scrape_by_date = scrape_by_date
        self.number_of_pages = number_of_pages

        self.list_of_ids = set(os.listdir(self.filepath))
        self.base_url = f"https://{city}.craigslist.org/d/apartments-housing-for-rent/search/apa?availabilityMode=0&s="
        self.today_base_url = f"https://{city}.craigslist.org/d/apartments-housing-for-rent/search/apa?availabilityMode=0&postedToday=1&s="

        self.use_rotating_link = use_rotating_link
        if use_rotating_link:
            self.sleep_time = 0.22  # assume 100 proxies, and all just about work

            self.curr_proxy = {
                "http": f"http://{user}-rotate:{password}@p.webshare.io:80/", 
                "https": f"http://{user}-rotate:{password}@p.webshare.io:80/"
                }
        elif proxies: 
            self.sleep_time = 20 / len(proxies) if 20 / len(proxies) > 0.015 else 0.015  # ~0.015s is the min for an avg spec Win PC
            
            self.curr_proxy = True
            self.avail_proxies = proxies  # proxies that can be used
            self.unavail_proxies = []  # proxies that are resting
        else: 
            self.sleep_time = 20  # defaults to 20  
            self.curr_proxy = False

        self.init_posts = 0  # how many posts are found on a page in total
        self.dup_posts = 0  # how many posts on a page were duplicates

        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(service=Service("./geckodriver"), options=options)

        self.updated_frontend = False  # generally assume that we aren't using the frontend that's showing up for sfbay


    def change_proxy(self):
        if self.use_rotating_link:
            return  # the rotating link changes the proxy every time, so we don't have to do anything for it
        elif self.curr_proxy:  # if there is a current proxy
            if not self.avail_proxies:  # if no more proxies are available
                self.avail_proxies = self.unavail_proxies  # move all proxies back into the available list
                self.unavail_proxies = []  # clear the unavailable list 

            proxy_holder = self.avail_proxies.pop(0)  # store the first proxy from avail_proxies to be made the curr_proxy
            self.curr_proxy = {"http": f"http://{user}:{password}@{proxy_holder}", "https": f"http://{user}:{password}@{proxy_holder}"}
            self.unavail_proxies.append(proxy_holder)  # add the curr_proxy to the unavailable list preemptively


    def get_page_of_posts(self, url):
        """ Takes the url of a page of search results and returns a dictionary of posts (after removing
            duplicate posts)

        Parameters
        ----------
            url (str): the url for a page of search results

        Returns
        ----------
            list: 
                dict: {result id: result url}
                bool: if there were no posts on the page
                bool: if the posts on the page weren't all duplicates
        """
        
        self.change_proxy()

        if not self.updated_frontend:
            try:
                page_data = get(url, proxies=self.curr_proxy)
            except Exception:
                time.sleep(10)
                page_data = get(url, proxies=self.curr_proxy)
                
            html_soup = BeautifulSoup(page_data.text, 'html.parser')
            search_results = html_soup.find("ul", id="search-results")
            posts = html_soup.find_all('li', class_='result-row')
            posts = [post for post in posts if not post.find("span", class_="nearby")]  # remove results from "nearby areas"

            if len(posts) == 0: 
                # a harvest moon is shown when we're out of results for non-daily; a train  is shown when we're out of results for daily
                if not html_soup.find("pre", id="moon") or not html_soup.find("pre", id="train"):  
                    body = html_soup.find("body")
                    if body and "blocked" in body.text:
                        if not self.use_rotating_link:  # if we aren't using the rotating link, we should remove the faulty proxy
                            self.unavail_proxies.remove(self.curr_proxy["http"].split("@")[-1])  # remove faulty proxy from this run (NOT FROM TXT FILE)
                            cprint(f"\nPROXY {self.curr_proxy} IS BLOCKED, AND HAS BEEN TAKEN OUT FOR THIS RUN. PLEASE REMOVE FROM PROXIES TXT", c="rB")
                            
                            new_sleep_time = 20 / (len(self.avail_proxies) + len(self.unavail_proxies))  # update the sleep time for new # of proxies
                            self.sleep_time = new_sleep_time if new_sleep_time >= 0.015 else 0.015
                            cprint(f"INCREASED sleep_time TO {self.sleep_time} SECONDS", c='y')
                        else:  # otherwise, we can't do anything about it
                            cprint(f"\nPROXY {self.curr_proxy} IS BLOCKED, BUT CAN'T BE REMOVED FROM THE RUN (SINCE use_rotating_link is True)", c="rB")
                        
                        return self.get_page_of_posts(url)  # return the results of a new run instead of continuing (proxy changed on L103)
                else:
                    cprint(f"No more search results!", c="y")
                    return [0, True, False]

            posts_dict = {}
            for post in posts:
                post_title = post.find('a', class_='result-title hdrlnk')
                post_id = post_title['id']
                post_url = post_title['href']
                posts_dict[post_id] = post_url

        else:
            # don't get URL again, or we reset the page we're on
            html_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            search_results = html_soup.find("div", class_="results cl-results-page cl-search-view-mode-gallery")
            posts = html_soup.find_all("li", class_="cl-search-result cl-search-view-mode-gallery")

            # don't know how to determine if a post is from a "nearby area" or not in the new UI
            # posts = [post for post in posts if not post.find("span", class_="nearby")]  # remove results from "nearby areas"

            posts_dict = {}
            for post in posts:
                post_url = post.find("a", class_="cl-gallery")["href"]
                post_id = post_url.split("/")[-1][:-5]
                posts_dict[post_id] = post_url

        self.init_posts = len(posts_dict)

        for post_id in self.list_of_ids:
            if post_id in posts_dict.keys():
                del posts_dict[post_id]  # if we've scraped a post before, don't scrape it again
            else:
                self.list_of_ids.add(post_id)  # otherwise, add it to the seen ids and scrape it

        updated_len = len(posts_dict)
        self.dup_posts = self.init_posts - updated_len

        return [posts_dict, self.init_posts == 0, updated_len != 0]
    

    def save_html_from_page(self, dictionary_of_posts):
        """ Takes a dictionary of posts (see: get_page_of_posts) and saves each post's html to a file

        Parameters
        ----------
            dictionary_of_posts (dict): a dictionary of posts of the form {id: url}

        Returns: 
            None
        """

        for key in tqdm(dictionary_of_posts.keys(), desc="Saving html of posts on current page...", leave=False):
            self.change_proxy()
            
            post_id = key
            url = dictionary_of_posts[key]
            filename = os.path.join(self.filepath, post_id)
            
            try:
                raw_html = get(url, proxies=self.curr_proxy)
            except Exception:
                time.sleep(10)
                raw_html = get(url, proxies=self.curr_proxy)
            
            with open(filename, 'w', encoding = 'utf-8') as file:
                file.write(raw_html.text)  # write the raw html to a file

            time.sleep(self.sleep_time)


    def get_posts_by_number(self):
        """ Scrapes a number of pages equal to number_of_pages (or until no posts remain); used to do an initial scrape
        """

        pbar = tqdm(total=self.number_of_pages, desc=f"Getting posts from {self.number_of_pages} page{'s' if self.number_of_pages > 1 else ''}...")
        for page in range(self.number_of_pages):
            page_url = self.base_url + str(page * 120)
            pbar.write(f"Getting a search result page at url '{page_url}'")
            gpp = self.get_page_of_posts(page_url)
            if gpp[1]: break  # if there are no more results/posts, break
            # don't care if we have duplicates, as we might need to get past/up to a few pages of duplicates

            pbar.write(f"Started with {self.init_posts} posts, {self.dup_posts} duplicates removed\n")
            current_page_dict = gpp[0]
            self.save_html_from_page(current_page_dict)

            pbar.update(1)


    def get_posts_from_today(self):
        """ Scrapes all posts made within the last 24 hours; used to do a cron scrape
        """

        current_page = 0
        page_url = self.today_base_url

        self.driver.get(page_url)
        time.sleep(3)
        page_soup = BeautifulSoup(self.driver.page_source, "html.parser")

        total_posts_today = page_soup.find("span", class_="totalcount")  # normal post range; craigslist may be/is updating frontend...
        if total_posts_today: 
            total_posts_str = total_posts_today.text
        else:
            total_posts_today = page_soup.find("span", class_="cl-page-number").text            
            total_posts_str = total_posts_today.split(" ")[-1]
            self.updated_frontend = True  # use updated frontend bs4 finds, etc.

        total_pages = ceil(float(total_posts_str.replace(",", "")) / 120)
        gpp = self.get_page_of_posts(page_url)

        with tqdm(total=total_pages, desc=f"Getting posts from today ({total_pages} page{'s' if total_pages > 1 else ''})...") as pbar:
            while not gpp[1] and gpp[2]:  # while there are results and they're not all duplicates
                current_page_dict = gpp[0]
                self.save_html_from_page(current_page_dict)
                
                if not self.updated_frontend:
                    current_page += 120
                    page_url = self.today_base_url + str(current_page)
                else:
                    next_page = self.driver.find_element(By.CSS_SELECTOR, "button.bd-button.cl-next-page.icon-only")
                    if next_page: next_page.click()
                    else: break
                
                gpp = self.get_page_of_posts(page_url)
                pbar.update(1)


    def scrape(self):
        """ Do a get_posts_from_today or get_posts_by_number based on the value of scrape_by_date; prints appropriate messages
        based on the result as well
        """

        right_now = str(date.today()) + " " + str(time.time())
        scrape_msg = f"Started scraping for {self.city} on: {right_now} | for all posts " 
        sleep_msg = f"Sleeping for {str(self.sleep_time)} seconds between every post get (prevents Craigslist ban)\n"

        # get search pages
        if self.scrape_by_date: 
            cprint(scrape_msg + f"today\n{sleep_msg}", c="c")
            self.get_posts_from_today()
        else: 
            cprint(scrape_msg + f"currently up. Should take ~{self.sleep_time * 0.8} hours\n{sleep_msg}", c="c")
            self.get_posts_by_number()

        cprint("Scraping completed!\n", c="gB")


#%%
def do_init_scrape(city: str, filepath: str=None, use_rotating_link: bool=False, proxies: str=None):
    scraper = CraigslistScraper(city, filepath=filepath, scrape_by_date=False, use_rotating_link=use_rotating_link, proxies=proxies)
    scraper.scrape()


def do_cron_scrape(city: str, filepath: str=None, use_rotating_link: bool=False, proxies: str=None):
    scraper = CraigslistScraper(city, filepath=filepath, use_rotating_link=use_rotating_link, proxies=proxies)
    scraper.scrape()
