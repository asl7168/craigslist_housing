# -*- coding: utf-8 -*-
"""
Created on Tue   Jun 01 2021
Updated on Thurs Jun 23 2022

@author: lmcox, asl7168

This script retrieves HTML pages for housing listings on Cragislist.

Some code and tips taken from: https://towardsdatascience.com/web-scraping-craigslist-a-complete-tutorial-c41cea4f4981
"""
#%%
from requests import get
from datetime import date
import time, os
from bs4 import BeautifulSoup

# note: any instance of the number 120 (being added, or dividing by) is due to Craigslist returning 120 results per page
class CraigslistScraper:
    """ Code to scrape html from craigslist and save, either as text files or in a csv
        the post data
    """

    def __init__(self, filepath=os.getcwd(), sleep_time=30, scrape_by_date=True, number_of_pages=1):
        self.filepath = filepath  # this should be where all html documents have BEEN saved
        self.list_of_ids = set(os.listdir(self.filepath))
        self.base_url = 'https://chicago.craigslist.org/d/apartments-housing-for-rent/search/apa?availabilityMode=0&s='
        self.today_base_url = 'https://chicago.craigslist.org/d/apartments-housing-for-rent/search/apa?availabilityMode=0&postedToday=1&s='
        self.number_of_pages = number_of_pages
        self.scrape_by_date = scrape_by_date
        self.sleep_time = sleep_time  # IF THIS IS TOO LOW, YOU MIGHT SEND TOO MANY REQUESTS AND BE BLOCKED BY CRAIGSLIST


    def check_url_status(self, url):
        """ Checks a url for errors; if there aren't any, returns the Request object of the url; otherwise, 
            outputs and logs the error

        Parameters
        ----------
            url (string)

        Returns
        ----------
            Request: the Request object of the parameter url
        """
        
        print(url)

        get_object = get(url)
        if get_object.ok:
            return get_object
        else:
            # create an error message
            error_status = "Error: " + url
            # get the time and date, for more info about the error/timed out
            thisdate = date.today()
            timestamp = time.time()
            # create a file title (including save path)
            filetitle = self.filepath + "error_log" + str(thisdate) + str(timestamp)
            # create a block of text to put in an error log file
            filetext = error_status + " | " + str(get_object)
            # prints out the error and time info to the screen
            print(error_status + ' at ' + str(thisdate) + str(timestamp))
            # saves a file with error information to the current directory
            with open(filetitle, 'w') as file:
                file.write(filetext)


    def get_page_of_posts(self, url):
        """ Takes the url of a page of search results and returns a dictionary of posts (after removing
            duplicate posts).

        Parameters
        ----------
            url (string): the url for a page of search results

        Returns
        ----------
            tuple: 
                dict: {result id: [result url, result title]}
                bool: if scraping is finished (all duplicates or no remaining posts to check)
        """
        
        print("\nGetting a search result page...")

        page_data = self.check_url_status(url)
        html_soup = BeautifulSoup(page_data.text, 'html.parser')
        posts = html_soup.find_all('li', class_= 'result-row')
        posts = posts if len(posts) <= 120 else posts[:int(html_soup.find(class_="rangeTo").getText())]

        posts_dict = {}
        for one_post in posts:
            one_post_title = one_post.find('a', class_='result-title hdrlnk')
            post_id = one_post_title['id']
            url = one_post_title['href']
            posts_dict[post_id] = [url, one_post_title]
        
        init_len = len(posts_dict)

        for post_id in self.list_of_ids:
            if post_id in posts_dict.keys():
                del posts_dict[post_id]

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

        print("Saving html...")

        for key in dictionary_of_posts.keys():
            post_id = key
            values = dictionary_of_posts[key]
            url = values[0]
            filename = os.path.join(self.filepath, post_id)
            raw_html = get(url)
            with open(filename, 'w', encoding = 'utf-8') as file:
                file.write(raw_html.text)


    def get_posts_by_number(self):        
        print(f"Calling get_posts_by_number (for {self.number_of_pages} pages)...")
        
        current_page = 0
        first = True 
        while (current_page / 120) < self.number_of_pages:
            if not first: 
                print(f"Sleeping for: {str(self.sleep_time)} seconds between search page calls. {str(time.time())}")
                time.sleep(self.sleep_time)

            page_url = self.base_url + str(current_page)
            current_page_dict = self.get_page_of_posts(page_url)[0]
            self.save_html_from_page(current_page_dict)
            current_page += 120


    """def get_pages_until_break(self):
        print("Calling get_pages_until_break...")
        #this function takes in a list of post ids and returns a dictionary of each post that isn't in the list of post ids
        #it does not limit the number of pages to search, so it will continue to loop through search pages
        #until the search page doesn't exist (e.g. throws an error)
        current_page = 0
        page_url = self.base_url + str(current_page)
        while get(page_url).ok == True:
            current_page_dict = self.get_page_of_posts(page_url)
            self.save_html_from_page(current_page_dict)
            current_page += 120
            page_url = self.base_url + str(current_page)
            print("Sleeping for: ", str(self.sleep_time), " seconds between search page calls. ", str(time.time()))
            time.sleep(self.sleep_time)"""
    

    def get_posts_from_today(self):
        print("Getting posts from today...")
        
        current_page = 0
        page_url = self.today_base_url
        gpp = self.get_page_of_posts(page_url)
        first = True

        while get(page_url).ok:
            if not gpp[1]: break 
            if not first: 
                print(f"Sleeping for: {str(self.sleep_time)} seconds between search page calls. {str(time.time())}")
                time.sleep(self.sleep_time)

            current_page_dict = gpp[0]
            self.save_html_from_page(current_page_dict)
            current_page += 120
            page_url = self.today_base_url + str(current_page)
            gpp = self.get_page_of_posts(page_url)


    def scrape(self):
        # get search pages
        if self.scrape_by_date: self.get_posts_from_today()
        else: self.get_posts_by_number()


#%%
if __name__ == '__main__':
    # print out start date/time
    # scraper = CraigslistScraper(filepath="html/", sleep_time=5)
    scraper = CraigslistScraper(filepath="html/", sleep_time=20, scrape_by_date=False, number_of_pages=5)
    # scraper = CraigslistScraper(scrape_by_date=True, filepath="/projects/p31502/projects/craigslist_housing/html/")
    right_now = str(date.today()) + " " + str(time.time())
    print(f"Started scraping on: {right_now} | for all posts made today" )
    scraper.scrape()
    print("Saving complete.")