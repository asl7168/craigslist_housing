# -*- coding: utf-8 -*-
"""
Created on Tue Jun  1 21:00:09 2021

@author: lmcox

This script retrieves HTML pages for housing listings on Cragislist.

Some code and tips taken from: https://towardsdatascience.com/web-scraping-craigslist-a-complete-tutorial-c41cea4f4981
"""
#%%
#import get to call a get request on the site
from requests import get
#import things that will help with making tidy data
from datetime import date
import time, os
#import beautiful soup to work with the text
from bs4 import BeautifulSoup


class CraigslistScraper:
    """Code to scrape html from craigslist and save, either as text files or in a csv
        the post data
    """

    def __init__(self, filepath=os.getcwd(), sleep_time=30, scrape_by_date=True, number_of_pages=1):
        self.filepath = filepath #this should be where all html documents have BEEN saved
        self.list_of_ids = set(os.listdir(self.filepath))
        self.base_url = 'https://chicago.craigslist.org/d/apartments-housing-for-rent/search/apa?availabilityMode=0&s='
        self.today_base_url = 'https://chicago.craigslist.org/d/apartments-housing-for-rent/search/apa?availabilityMode=0&postedToday=1&s='
        self.number_of_pages = number_of_pages
        self.scrape_by_date = scrape_by_date
        self.sleep_time = sleep_time

    def check_url_status(self, url):
        #this function takes in a url,
        #calls the get function (requests.get) on the url
        #checks where there's a 4xx or 5xx error, and 
        #returns either:
        #if there isn't an error, the get object (i.e. functions like running requests.get(url))
        #if there is an error, an error message
            #and writes the error to a file
            #and ends the loop - ending data collection
        print(url)
        get_object = get(url)
        if get_object.ok:
            return get_object
        else:
            #create an error message
            error_status = "Error: " + url
            #get the time and date, for more info about the error/timed out
            thisdate = date.today()
            timestamp = time.time()
            #create a file title (including save path)
            filetitle = self.filepath + "error_log" + str(thisdate) + str(timestamp)
            #create a block of text to put in an error log file
            filetext = error_status + " | " + str(get_object)
            #prints out the error and time info to the screen
            print(error_status + ' at ' + str(thisdate) + str(timestamp))
            #saves a file with error information to the current directory
            with open(filetitle, 'w') as file:
                file.write(filetext)

    def get_posts(self, one_page_of_results):
        print("Getting individual posts...")
        #this function takes in the text of search result page, beautifulsoup'd up already, and returns a dictionary
        #of all the posts' titles, urls, ids, with the post id as the key
        post_dict = {}
        for one_post in one_page_of_results:
            one_post_title = one_post.find('a',class_='result-title hdrlnk')
            post_id = one_post_title['id']
            url = one_post_title['href']
            post_dict[post_id] = [url, one_post_title]
        return post_dict

    def check_id_list(self, dictionary_of_posts):
        how_many = len(dictionary_of_posts)
        for post_id in self.list_of_ids:
            if post_id in dictionary_of_posts.keys():
                del dictionary_of_posts[post_id]
            else:
                pass
        num_remaining = len(dictionary_of_posts)
        print(f"Started with {how_many}, {how_many-num_remaining} removed as already downloaded")
        return dictionary_of_posts

    def get_page_of_posts(self, url):
        print("Getting a search result page...")
        #this function takes a craigslist search result page url and returns a dictionary of all posts on that page,
        #using the get_posts function
        #it then deletes any for which the post_id is one we already have
        page_data = self.check_url_status(url)
        html_soup = BeautifulSoup(page_data.text, 'html.parser')
        posts = html_soup.find_all('li', class_= 'result-row')
        current_page_dict = self.get_posts(posts)
        current_page_dict = self.check_id_list(current_page_dict)
        return current_page_dict
    
    def get_pages_by_number(self):
        print("Calling get_pages_by_number...")
        #this function takes a number of pages, and returns a dictionary of each post on all of those pages
        current_page = 0
        while (current_page/120) <= self.number_of_pages:
            page_url = self.base_url + str(current_page)
            current_page_dict = self.get_page_of_posts(page_url)
            self.save_html_from_page(current_page_dict)
            current_page += 120


    def get_pages_until_break(self):
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
            time.sleep(self.sleep_time)

    def get_posts_from_today(self):
        print("Getting posts from today...")
        current_page = 0
        page_url = self.today_base_url
        while get(page_url).ok == True:
            current_page_dict = self.get_page_of_posts(page_url)
            self.save_html_from_page(current_page_dict)
            current_page += 120
            page_url = self.today_base_url + str(current_page)
            print("Sleeping for: ", str(self.sleep_time), " seconds between search page calls. ", str(time.time()))
            time.sleep(self.sleep_time)

    def save_html_from_page(self, dictionary_of_posts):
        print("Saving html...")
        #takes in a dictionary of posts, where key = post_id and values = url, post title
        for key in dictionary_of_posts.keys():
            post_id = key
            values = dictionary_of_posts[key]
            url = values[0]
            filename = os.path.join(self.filepath, post_id)
            raw_html = get(url)
            with open(filename, 'w', encoding = 'utf-8') as file:
                file.write(raw_html.text)

    def scrape(self):
        #get search pages
        if self.scrape_by_date==True:
            self.get_posts_from_today()
        else:
            self.get_pages_by_number()


#%%
if __name__ == '__main__':
    #print out start date/time
    scraper = CraigslistScraper(scrape_by_date=True, filepath="/projects/p31079/projects/craigslist_housing/html/")
    right_now = str(date.today()) + " " + str(time.time())
    print("Started scraping on: ", right_now, " | for all posts made today" )
    scraper.scrape()
    print("Saving complete.")