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
import sys

class FinnkodeScraper:
    def __init__(self, url):
        self.url = url
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")
        
        options.add_experimental_option('excludeSwitches', ['enable-logging'])  # This suppresses the 'DevTools listening on...' message.
        
        # On Unix-like systems, use '/dev/null'. For Windows, use 'NUL'.
        sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)
        
        self.driver = webdriver.Chrome(options=options)
    def get_finnkodes_and_links(self):
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
    
    #Tar ikke alltid inn pris, legge til condition for månedspris
    def extract_price(self):
         
        numeric_price = None
        try:
            price_section = self.driver.find_element(By.CSS_SELECTOR, "section.panel.u-mt32:not(.import-decoration) .flex-wrapper .flex-wrapper__unit .u-t3")
            #print("DEBUG: Price element HTML:", price_section.get_attribute('outerHTML'))  # This will print the HTML of the price element
            price = self.driver.execute_script('return arguments[0].textContent;', price_section)
            #exclude chars (kr)
            numeric_price = re.sub("[^\d]", "", price)  # This removes all non-digit charactersprint("Extracted Numeric Price:", numeric_price)
        except Exception as e:
            print(f"An error occurred while trying to extract the price: {e}")
            numeric_price = None
            '''  
            price_section = self.driver.find_element(By.CSS_SELECTOR, "section.panel.u-mt32:not(.import-decoration) .flex-wrapper .flex-wrapper__unit .u-t3")
            print("DEBUG: Price element HTML:", price_section.get_attribute('outerHTML'))  # This will print the HTML of the price element
            price = self.driver.execute_script('return arguments[0].textContent;', price_section)
            #exclude chars (kr)
            numeric_price = re.sub("[^\d]", "", price)
            '''   
        return numeric_price
    #problemer i enkelte tilfeller
    def extract_model_name(self):
        try:
        # Find the h1 tag which we're assuming contains the model name
            model_name_element = self.driver.find_element(By.TAG_NAME, 'h1')
            print("DEBUG: Model name element HTML:", model_name_element.get_attribute('outerHTML'))  # Debugging

            # Execute JavaScript to return the text content of the model name element
            model_name = self.driver.execute_script('return arguments[0].textContent;', model_name_element)
            model_name = model_name.strip()  # Remove any extra whitespace from the text
        except Exception as e:
            print(f"An error occurred while extracting the model name: {e}")
            model_name = "Model name could not be extracted."

        return model_name
    def extract_finnkode(self):
            # Extract the Finnkode from the URL
        finnkode = self.url.split('finnkode=')[-1].split('&')[0]
        return finnkode
    def close(self):
        self.driver.close()  
def insert_car(conn, finnkode, car_name, link, price):
    sql = 'INSERT INTO Car(Finnkode, car_name, Link, Price) VALUES(?,?,?,?)'
    cur = conn.cursor()
    cur.execute(sql, (finnkode, car_name, link, price))
    conn.commit()

def insert_description(conn, finnkode, description):
    sql = 'INSERT INTO Beskrivelse(Finnkode, Description_Text) VALUES(?,?)'
    cur = conn.cursor()
    cur.execute(sql, (finnkode, description))
    conn.commit()

def insert_specifications(conn, finnkode, specifications):
    sql = 'INSERT INTO Spesifikasjoner(Finnkode, Specifications) VALUES(?,?)'
    specifications_json = json.dumps(specifications)
    cur = conn.cursor()
    cur.execute(sql, (finnkode, specifications_json))
    conn.commit()

def insert_equipment(conn, finnkode, equipment_list):
    sql = 'INSERT INTO Utstyr(Finnkode, Equipment) VALUES(?,?)'
    equipment_json = json.dumps(equipment_list)
    cur = conn.cursor()
    cur.execute(sql, (finnkode, equipment_json))
    conn.commit()

def element_exists(cursor, table, field, data):
    query = f"SELECT 1 FROM {table} WHERE {field} = ?"
    cursor.execute(query, (data,))
    result = cursor.fetchone()
    return result is not None

      
if __name__ == "__main__":
    
    #---Extracting information of one page----
    search_url = "https://www.finn.no/car/used/search.html"
    scraper = FinnkodeScraper(search_url)
    database = "../data_gathering/cars.db"
    
    links = scraper.get_finnkodes_and_links()[:5]  # Adjust to fetch only the first 10 links
    print(links)
    
    print(links[0])
    code = []
    
    for finnkode, link in links:
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        if element_exists(cursor, 'Car', 'Finnkode',finnkode):
            print("Element exists")
            
        else:
            try:
                print(f"Adding Car with finnkode: {finnkode} ")
                
                
                car_scraper = FinnkodeScraper(link)
                finncode = car_scraper.extract_finnkode()
                car_scraper.driver.get(link)
                #page_html = car_scraper.driver.find_element(By.TAG_NAME, 'body').get_attribute('outerHTML')
                #print("DEBUG: Page HTML:", page_html)
                price = car_scraper.extract_price()
                print(f"pris{price}")
                
                if price is None:
                    continue
                description = car_scraper.extract_description()
                
                equipment_list = car_scraper.extract_equipment()
                specifications = car_scraper.extract_car_specs()
                
                car_name = car_scraper.extract_model_name()
                
                car_scraper.close()
                
                with connection:
                    insert_car(connection, finncode, car_name, link, price)
                    insert_description(connection, finncode, description)
                    insert_specifications(connection, finncode, specifications)
                    #print(car_info['specifications'])
                    insert_equipment(connection, finncode, equipment_list)
                print(f"Added Finnkode: {finncode}, Link: {link}, Price: {price}")
            except Exception as e:
                print(f"An error occurred while scraping {finncode}: {e}")

            # Wait for the page to load
        time.sleep(10)
    print(len(links), "Cars added.")
                 