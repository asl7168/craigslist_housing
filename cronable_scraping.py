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
from tqdm import tqdm, trange
from math import ceil
from webshare_credentials import user, password

# note: any instance of the number 120 (being added, or dividing by) is due to Craigslist returning 120 results per page
class CraigslistScraper:
    """ Code to scrape html from craigslist and save, either as text files or in a csv
        the post data
    """

    def __init__(self, city, filepath: str=None, sleep_time: int=20, scrape_by_date: bool=True, number_of_pages: int=1, proxies: list=None):
        self.filepath = filepath + "/" + city if filepath else f"../../html/{city}"  # this should be where all html documents have BEEN saved
        if not os.path.exists(self.filepath): os.makedirs(self.filepath)
        
        self.sleep_time = sleep_time  # IF THIS IS TOO LOW, YOU MIGHT SEND TOO MANY REQUESTS AND BE BLOCKED BY CRAIGSLIST
        self.scrape_by_date = scrape_by_date
        self.number_of_pages = number_of_pages

        self.list_of_ids = set(os.listdir(self.filepath))
        self.base_url = f"https://{city}.craigslist.org/d/apartments-housing-for-rent/search/apa?availabilityMode=0&s="
        self.today_base_url = f"https://{city}.craigslist.org/d/apartments-housing-for-rent/search/apa?availabilityMode=0&postedToday=1&s="

        if proxies: 
            self.curr_proxy = dict()
            self.avail_proxies = proxies
            self.unavail_proxies = []
        else: 
            self.curr_proxy = False


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
        
        print(f"\n\nGetting a search result page at url '{url}'...")

        try:
            page_data = get(url, proxies=self.curr_proxy)
        except:
            time.sleep(10)
            page_data = get(url, proxies=self.curr_proxy)
            
        html_soup = BeautifulSoup(page_data.text, 'html.parser')
        posts = html_soup.find_all('li', class_= 'result-row')

        posts_dict = {}
        for post in posts:
            post_title = post.find('a', class_='result-title hdrlnk')
            post_id = post_title['id']
            url = post_title['href']
            posts_dict[post_id] = url
        
        init_len = len(posts_dict)

        for post_id in self.list_of_ids:
            if post_id in posts_dict.keys():
                del posts_dict[post_id]
            else:
                self.list_of_ids.add(post_id)

        updated_len = len(posts_dict)
        print(f"Started with {init_len} posts, {init_len - updated_len} duplicates removed")

        return (posts_dict, updated_len != 0)
    

    def save_html_from_page(self, dictionary_of_posts):
        """ Takes a dictionary of posts (see: get_page_of_posts) and saves each post's html to a file.

        Parameters
        ----------
            dictionary_of_posts (dict): a dictionary of posts

        Returns: 
            None
        """

        for key in tqdm(dictionary_of_posts.keys(), desc="Saving html of posts on current page..."):
            if not self.avail_proxies:
                self.avail_proxies = self.unavail_proxies
                self.unavail_proxies = []

            proxy_holder = self.avail_proxies.pop(0)
            self.curr_proxy = {"http": f"http://{user}:{password}@{proxy_holder}", "https": f"http://{user}:{password}@{proxy_holder}"}
            self.unavail_proxies.append(proxy_holder)
            
            post_id = key
            url = dictionary_of_posts[key]
            filename = os.path.join(self.filepath, post_id)
            
            try:
                raw_html = get(url, proxies=self.curr_proxy)
            except:
                time.sleep(10)
                raw_html = get(url, proxies=self.curr_proxy)
            
            with open(filename, 'w', encoding = 'utf-8') as file:
                file.write(raw_html.text)

            time.sleep(self.sleep_time)


    def get_posts_by_number(self):        
        for page in trange(self.number_of_pages, desc=f"Getting posts from {self.number_of_pages} page{'s' if self.number_of_pages > 1 else ''}..."):
            page_url = self.base_url + str(page * 120)
            current_page_dict = self.get_page_of_posts(page_url)[0]
            self.save_html_from_page(current_page_dict)


    def get_posts_from_today(self):  # TODO: update the logic of how this works; don't need the extra get in the while, clean this whole block up
        current_page = 0
        page_url = self.today_base_url
        total_pages = ceil(float(BeautifulSoup(get(page_url, proxies=self.curr_proxy).text, 'html.parser').find("span", class_="totalcount").text) / 120)
        gpp = self.get_page_of_posts(page_url)

        with tqdm(total=total_pages, desc=f"Getting posts from today ({total_pages} page{'s' if total_pages > 1 else ''})...") as pbar:
            while get(page_url, proxies=self.curr_proxy).ok:
                if not gpp[1]: break

                current_page_dict = gpp[0]
                self.save_html_from_page(current_page_dict)
                current_page += 120
                page_url = self.today_base_url + str(current_page)
                gpp = self.get_page_of_posts(page_url)

                pbar.update(1)


    def scrape(self):
        print(f"Sleeping for {str(self.sleep_time)} seconds between every post get (prevents Craigslist ban)\n")

        # get search pages
        if self.scrape_by_date: self.get_posts_from_today()
        else: self.get_posts_by_number()

        print("Scraping completed!")


#%%
def do_init_scrape(city: str, filepath: str=None, sleep_time: int=20, proxies: str=None):
    right_now = str(date.today()) + " " + str(time.time())
    print(f"Started scraping for {city} on: {right_now} | for all posts currently up. Should take ~{sleep_time * 0.8} hours")
    
    scraper = CraigslistScraper(city, filepath=filepath, sleep_time=sleep_time, scrape_by_date=False, number_of_pages=30, proxies=proxies)
    scraper.scrape()
    
    print("Saving complete.")


def do_cron_scrape(city: str, filepath: str=None, sleep_time: int=20, proxies: str=None):
    right_now = str(date.today()) + " " + str(time.time())
    print(f"Started scraping for {city} on: {right_now} | for all posts made today")
    
    scraper = CraigslistScraper(city, filepath=filepath, sleep_time=sleep_time, proxies=proxies)
    scraper.scrape()
    
    print("Saving complete.")
