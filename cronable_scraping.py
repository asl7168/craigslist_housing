# -*- coding: utf-8 -*-
"""
Created on Tue   Jun 01   2021
Updated          Jun-July 2022

@author: lmcox, asl7168

This script retrieves HTML pages for housing listings on Cragislist.

Some code and tips taken from: https://towardsdatascience.com/web-scraping-craigslist-a-complete-tutorial-c41cea4f4981
"""
#%%
from requests import get
from datetime import date
import time, os
from bs4 import BeautifulSoup
from tqdm import tqdm
from math import ceil
from webshare_credentials import user, password
from cprint import cprint

# note: any instance of the number 120 (being added, or dividing by) is due to Craigslist returning 120 results per page
class CraigslistScraper:
    """ Code to scrape html from craigslist and save, either as text files or in a csv
        the post data
    """

    def __init__(self, city, filepath: str=None, scrape_by_date: bool=True, number_of_pages: int=1, proxies: list=None):
        self.city = city
        self.filepath = filepath + "/" + city if filepath else f"../../html/{city}"  # this should be where all html documents have BEEN saved
        if not os.path.exists(self.filepath): os.makedirs(self.filepath)
        
        self.scrape_by_date = scrape_by_date
        self.number_of_pages = number_of_pages

        self.list_of_ids = set(os.listdir(self.filepath))
        self.base_url = f"https://{city}.craigslist.org/d/apartments-housing-for-rent/search/apa?availabilityMode=0&s="
        self.today_base_url = f"https://{city}.craigslist.org/d/apartments-housing-for-rent/search/apa?availabilityMode=0&postedToday=1&s="

        if proxies: 
            self.sleep_time = 20 / len(proxies) if 20 / len(proxies) > 0.015 else 0.015  # ~0.015s is the min for an avg spec Win PC
            
            self.curr_proxy = True
            self.avail_proxies = proxies
            self.unavail_proxies = []
        else: 
            self.sleep_time = 20  # defaults to 20  
            self.curr_proxy = False

        self.init_posts = 0
        self.dup_posts = 0


    def change_proxy(self):
        if self.curr_proxy:
            if not self.avail_proxies:
                self.avail_proxies = self.unavail_proxies
                self.unavail_proxies = []

            proxy_holder = self.avail_proxies.pop(0)
            self.curr_proxy = {"http": f"http://{user}:{password}@{proxy_holder}", "https": f"http://{user}:{password}@{proxy_holder}"}
            self.unavail_proxies.append(proxy_holder)


    def get_page_of_posts(self, url):
        """ Takes the url of a page of search results and returns a dictionary of posts (after removing
            duplicate posts).

        Parameters
        ----------
            url (string): the url for a page of search results

        Returns
        ----------
            tuple: 
                dict: {result id: result url}
                bool: if scraping is finished (all duplicates or no remaining posts to check)
        """
        
        self.change_proxy()

        try:
            page_data = get(url, proxies=self.curr_proxy)
        except:
            time.sleep(10)
            page_data = get(url, proxies=self.curr_proxy)
            
        html_soup = BeautifulSoup(page_data.text, 'html.parser')
        posts = html_soup.find_all('li', class_= 'result-row')
        
        if len(posts) == 0: 
            # a harvest moon is shown when we're out of results for non-daily; a train  is shown when we're out of results for daily
            if not html_soup.find("pre", id="moon") or not html_soup.find("pre", id="train"):  
                body = html_soup.find("body")
                if body and "blocked" in body.text:
                    self.unavail_proxies.remove(self.curr_proxy["http"].split("@")[-1])  # remove faulty proxy from this run (NOT FROM TXT FILE)
                    cprint(f"\nPROXY {self.curr_proxy} IS BLOCKED, AND HAS BEEN TAKEN OUT FOR THIS RUN. PLEASE REMOVE FROM PROXIES TXT", c="rB")
                    
                    new_sleep_time = 20 / (len(self.avail_proxies) + len(self.unavail_proxies))
                    self.sleep_time = new_sleep_time if new_sleep_time >= 0.015 else 0.015
                    cprint(f"INCREASED sleep_time TO {self.sleep_time} SECONDS", c='y')
                    
                    return self.get_page_of_posts(url)  # return the results of a new run instead of continuing (proxy changed on L74)
            else:
                cprint(f"No more search results!", c="y")
                return [0, True, False]

        posts_dict = {}
        for post in posts:
            post_title = post.find('a', class_='result-title hdrlnk')
            post_id = post_title['id']
            url = post_title['href']
            posts_dict[post_id] = url
        
        self.init_posts = len(posts_dict)

        for post_id in self.list_of_ids:
            if post_id in posts_dict.keys():
                del posts_dict[post_id]
            else:
                self.list_of_ids.add(post_id)

        updated_len = len(posts_dict)
        self.dup_posts = self.init_posts - updated_len

        return [posts_dict, self.init_posts == 0, updated_len != 0]
    

    def save_html_from_page(self, dictionary_of_posts):
        """ Takes a dictionary of posts (see: get_page_of_posts) and saves each post's html to a file.

        Parameters
        ----------
            dictionary_of_posts (dict): a dictionary of posts

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
                file.write(raw_html.text)

            time.sleep(self.sleep_time)


    def get_posts_by_number(self):        
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
        current_page = 0
        page_url = self.today_base_url
        total_pages = ceil(float(BeautifulSoup(get(page_url).text, "html.parser").find("span", class_="totalcount").text) / 120)
        gpp = self.get_page_of_posts(page_url)

        with tqdm(total=total_pages, desc=f"Getting posts from today ({total_pages} page{'s' if total_pages > 1 else ''})...") as pbar:
            while not gpp[1] and gpp[2]:  # while there are results and they're not all duplicates
                current_page_dict = gpp[0]
                self.save_html_from_page(current_page_dict)
                current_page += 120
                page_url = self.today_base_url + str(current_page)
                gpp = self.get_page_of_posts(page_url)

                pbar.update(1)


    def scrape(self):
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
def do_init_scrape(city: str, filepath: str=None, proxies: str=None):
    scraper = CraigslistScraper(city, filepath=filepath, scrape_by_date=False, number_of_pages=30, proxies=proxies)
    scraper.scrape()


def do_cron_scrape(city: str, filepath: str=None, proxies: str=None):
    scraper = CraigslistScraper(city, filepath=filepath, proxies=proxies)
    scraper.scrape()
