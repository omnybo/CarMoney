import json
import os
import sqlite3
import time
import re
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class FinnkodeScraper:
    def __init__(self, url):
        self.url = url
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)
    def get_finnkodes_links_and_prices(self):
        data = []
        # Navigate to the provided URL
        self.driver.get(self.url)
        # Wait for <article> elements with specific XPath to appear
        try:
            articles = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//article[contains(@class, 'sf-search-ad')]"))
            )
        except TimeoutException:
            print("The articles were not found within the given time frame.")
            return data

        # Wait for the page to load
        time.sleep(3)
        # Extract data: finnkode, link
        articles = self.driver.find_elements(By.XPATH, "//article[contains(@class, 'sf-search-ad')]")
        for article in articles:
            link_element = article.find_element(By.XPATH, ".//a[contains(@href, 'finnkode=')]")
            href = link_element.get_attribute("href")
            finnkode = href.split("finnkode=")[1].split("&")[0]
            
            print(f"Finnkode: {finnkode}, Link:{href}")
            data.append((finnkode, href))
        return data
    
    def extract_description(self):
        # Navigate to the provided URL
        self.driver.get(self.url)
        time.sleep(2)  # Ensure all elements are loaded, might require fine-tuning

        try:
            # Find the section with 'Beskrivelse' and extract the following sibling <p>'s innerHTML
            section = self.driver.find_element(By.CSS_SELECTOR, "section.panel.u-mt32.import-decoration")
            description_container = section.find_element(By.XPATH, ".//h2[contains(text(),'Beskrivelse')]/following-sibling::p")
            description = description_container.get_attribute("innerHTML")
        except Exception as e:
            print(f"An error occurred while extracting description: {e}")
            description = "Description could not be extracted."

        return description
    def extract_car_specs(self):
        self.driver.get(self.url)
        try:
            # Use find_elements to get a list of all matching elements
            elements = self.driver.find_elements(By.CSS_SELECTOR, "section.panel.panel--bleed.summary-icons .media__body")

            specs = {}
            labels = []
            values = []
            for element in elements:
                # Assuming each media__body contains exactly one label (non-strong text) and one value (strong text)
                label_elements = element.find_elements(By.CSS_SELECTOR, "div:not(.u-strong)")
                value_elements = element.find_elements(By.CSS_SELECTOR, "div.u-strong")
                
                for label_element, value_element in zip(label_elements, value_elements):
                    # Use JavaScript to retrieve text content, which may include handling special characters like non-breaking spaces
                    label_text = self.driver.execute_script("return arguments[0].textContent;", label_element).strip()
                    value_text = self.driver.execute_script("return arguments[0].textContent;", value_element).strip()

                    # Replace non-breaking spaces and standardize spacing, if necessary
                    value_text = value_text.replace('\xa0', ' ')

                    # Store the label and its corresponding value in the specs dictionary
                    specs[label_text] = value_text
            return specs
        except Exception as e:
            print(f"An error occurred while extracting car specs: {e}")
            return {}

    def extract_equipment(self):
        self.driver.get(self.url)
        equipment_list = []  # Initialize an empty list to hold the equipment items' HTML
        try:
            # Use find_elements to get a list of all matching elements
            elements = self.driver.find_elements(By.CSS_SELECTOR, "section.panel.u-mt32:not(.import-decoration) .list.u-col-count2.u-col-count3from990 li")

            for element in elements:
                equipment_html = element.get_attribute('innerHTML')
                equipment_list.append(equipment_html)
                #print("DEBUG: Equipment HTML:", equipment_html)  # This will print the HTML of each equipment item

        except Exception as e:
            print(f"An error occurred while extracting equipment: {e}")
        
        return equipment_list
    def close(self):
        self.driver.close()  
        
if __name__ == "__main__":
    search_url = "https://www.finn.no/car/used/search.html"
    # Create an instance of the scraper for the search page
    search_scraper = FinnkodeScraper(search_url)
    listings_data = search_scraper.get_finnkodes_links_and_prices()  # Retrieve all listings on the search page
    
    for finnkode, link in listings_data:
        # For each listing, create a new scraper instance for the detailed car page
        car_scraper = FinnkodeScraper(link)
        description = car_scraper.extract_description()
        specs = car_scraper.extract_car_specs()
        equipment_list = car_scraper.extract_equipment()
        car_scraper.close()
    
    # Close the search page scraper
    search_scraper.close()