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
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)
        
        self.driver = webdriver.Chrome(options=options)
    def get_finnkodes_and_links(self):
        data = []
        #Navigate to the provided URL
        self.driver.get(self.url)
        # Wait for <article> elements based on XPATH
        try:
            articles = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//article[contains(@class, 'sf-search-ad')]"))
            )
        except TimeoutException:
            print("The articles were not found within the given time frame.")
            return data

        #Wait for the page to load
        time.sleep(3)
        # Extract data: link and finnkode
        articles = self.driver.find_elements(By.XPATH, "//article[contains(@class, 'sf-search-ad')]")
        for article in articles:
            link_element = article.find_element(By.XPATH, ".//a[contains(@href, 'finnkode=')]")
            href = link_element.get_attribute("href")
            finnkode = href.split("finnkode=")[1].split("&")[0]
            
            print(f"Finnkode: {finnkode}, Link:{href}")
            data.append((finnkode, href))
        return data
    
    def extract_description(self):
        #Navigate to the provided URL
        self.driver.get(self.url)
        time.sleep(2)

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
            #Use find_elements to get a list of all matching elements
            #get panel of km, modellår, girkasse and drivstoff + the media__body with each specs label and its value
            elements = self.driver.find_elements(By.CSS_SELECTOR, "section.panel.panel--bleed.summary-icons .media__body")

            specs = {}
            labels = []
            values = []
            for element in elements:
                #Extract Specifications Label
                label_elements = element.find_elements(By.CSS_SELECTOR, "div:not(.u-strong)")
                #Extract  Specification Value
                value_elements = element.find_elements(By.CSS_SELECTOR, "div.u-strong")
                
                for label_element, value_element in zip(label_elements, value_elements):
                    #Extract text content from each element
                    label_text = self.driver.execute_script("return arguments[0].textContent;", label_element).strip()
                    value_text = self.driver.execute_script("return arguments[0].textContent;", value_element).strip()

                    #Replace non-breaking spaces, excessive whitespaces and extract actual value
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
            # Use find_elements to get a list of elements matching the specified CSS selector
            elements = self.driver.find_elements(By.CSS_SELECTOR, "section.panel.u-mt32:not(.import-decoration) .list.u-col-count2.u-col-count3from990 li")

            for element in elements:
                equipment_html = element.get_attribute('innerHTML')
                equipment_list.append(equipment_html)
                #Debug equipment HTML
                #equipment_html = element.get_attribute('innerHTML')
                #print("DEBUG: Equipment HTML:", equipment_html)  # This will print the HTML of each equipment item

        except Exception as e:
            print(f"An error occurred while extracting equipment: {e}")
        
        return equipment_list
    
    def extract_price(self):
         
        numeric_price = None
        try:
            #locate price element using class name
            price_section = self.driver.find_element(By.CSS_SELECTOR, "section.panel.u-mt32:not(.import-decoration) .flex-wrapper .flex-wrapper__unit .u-t3")
            #print("DEBUG: Price element HTML:", price_section.get_attribute('outerHTML'))  # This will print the HTML of the price element
            #Retrieve innerHTML (which includes both currency symbol) and parse it into float
            price = self.driver.execute_script('return arguments[0].textContent;', price_section)
            #exclude chars (kr)
            numeric_price = re.sub("[^\d]", "", price)  # This removes all non-digit charactersprint("Extracted Numeric Price:", numeric_price)
        
        except NoSuchElementException:
        #Element not found, set numeric_price to None
            print("Price element not found, skipping...")
        
        except Exception as e:
            print(f"An error occurred while trying to extract the price: {e}")
            numeric_price = None
              
        return numeric_price
    def extract_model_name(self):
        try:
        # Find the h1 tag which we're assuming contains the car name
            car_name_element = self.driver.find_element(By.TAG_NAME, 'h1')
            #print("DEBUG: Model name element HTML:", car_name.get_attribute('outerHTML'))  # Debugging

            #Execute JavaScript to return the text content of the car name element
            car_name = self.driver.execute_script('return arguments[0].textContent;', car_name_element)
            car_name = car_name.strip()  #Remove any extra whitespace from the text
        except Exception as e:
            print(f"An error occurred while extracting the model name: {e}")
            car_name = "Model name could not be extracted."

        return car_name
    
    def extract_price_from_smidig_bilhandel(self):
        #Smidig bilhandel price element located in a shadow DOM, using Java Sript execution
        #to access the inner HTML of the element
        try:
            shadow_host = self.driver.find_element(By.CSS_SELECTOR, "tjm-ad-entry")
            shadow_root = self.driver.execute_script('return arguments[0].shadowRoot', shadow_host)
            price_element = shadow_root.find_element(By.CSS_SELECTOR, "h2[data-testid='price']")
            
            #
            price_text = price_element.get_attribute("textContent").strip()
            price = re.sub(r"[^\d]", "", price_text)
            return price
        except NoSuchElementException:
            print("Shadow DOM price element not found on the page.")
            return None
    
    def extract_specs_list(self):
        try:
        #Use find_elements to get a list of all matching elements
            label_elements = self.driver.find_elements(By.CSS_SELECTOR, "section.panel.u-mt32 .list-descriptive.u-col-count2.u-col-count3from990 dt")
            value_elements = self.driver.find_elements(By.CSS_SELECTOR, "section.panel.u-mt32 .list-descriptive.u-col-count2.u-col-count3from990 dd")

            specs = {}
            for label_element, value_element in zip(label_elements, value_elements):
                
                label_text = label_element.get_attribute("textContent").strip()
                value_text = value_element.get_attribute("textContent").strip()

                #Replace non-breaking spaces and standardize spacing, if necessary
                value_text = value_text.replace('\xa0', ' ').replace('\n','').strip()
                cleaned_text = re.sub(r'\s+', ' ', value_text).strip()
                # Store the label and its corresponding value in the specs dictionary
                specs[label_text] = cleaned_text
            return specs
        except Exception as e:
            print(f"An error occurred while extracting car specs: {e}")
            return {}
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

def insert_beskrivelse(conn, finnkode, description):
    sql = 'INSERT INTO Beskrivelse(Finnkode, Description_Text) VALUES(?,?)'
    equipment_json = json.dumps(description)
    cur = conn.cursor()
    cur.execute(sql, (finnkode, description))
    conn.commit()

def element_exists(cursor, table, field, data):
    query = f"SELECT 1 FROM {table} WHERE {field} = ?"
    cursor.execute(query, (data,))
    result = cursor.fetchone()
    return result is not None

def merge_dicts(dict1,dict2):
    merged = dict1.copy()    
    for key, value in dict2.items():
        if key not in merged or merged[key] != value:
            merged[key] = value
    return merged
     
if __name__ == "__main__":
    database = "../data_gathering/cars_database.db"
    try:
        connection = sqlite3.connect(database)
        print("Successfully connected to the database.")
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
        sys.exit(1) 
        
    links = []
    connection = sqlite3.connect(database)
    counter = 0
    change = 1
    #extract based on price and published:
    #for x in range(50000,1500000,change):
        #for i in range(50):
        #URL = "https://www.finn.no/car/used/search.html?page="+str(i+1)+"&price_from="+str(x+1)+"&price_to="+str(x+change)+"&sales_form=1&sort=PUBLISHED_DESC"

    for x in range(2017,3000,change):
        for i in range(50):
            #extract based on year:
            URL = "https://www.finn.no/car/used/search.html?page="+str(i+1)+"&sales_form=1&sort=PUBLISHED_DESC"+"&year_from="+str(x+1)+"&year_to="+str(x+change)
            print('Scraping page:')
        
            scraper = FinnkodeScraper(URL)
            data = scraper.get_finnkodes_and_links()

            if not data or len(data) <=1:
                break
            scraper.close()
        
            links.extend(data)
            for finnkode, link in links:
                cursor = connection.cursor()
                if not element_exists(cursor,'Car','Finnkode',finnkode):
                    try:
                        print(f"Adding Car with finnkode: {finnkode} ")
                        
                        car_scraper = FinnkodeScraper(link)
                        finncode = car_scraper.extract_finnkode()
                        
                        
                        car_scraper.driver.get(link)
                        #page_html = car_scraper.driver.find_element(By.TAG_NAME, 'body').get_attribute('outerHTML')
                        #print("DEBUG: Page HTML:", page_html)
                        price = car_scraper.extract_price()
                            
                        if not price:
                            price = car_scraper.extract_price_from_smidig_bilhandel()
                        specifications = car_scraper.extract_car_specs()
                        car_name = car_scraper.extract_model_name()
                        car_specs_list = car_scraper.extract_specs_list()
                        combined_specs = merge_dicts(specifications, car_specs_list)
                        equipment_list = car_scraper.extract_equipment()
                        description =  car_scraper.extract_description()
                        #links.append(price)
                        car_scraper.close()
                        
                        insert_car(connection, finnkode, car_name, link, price)
                        print('successfully inserted car')
                        insert_specifications(connection, finnkode, combined_specs)
                        insert_equipment(connection, finnkode, equipment_list)
                        insert_description(connection, finnkode, description)
                        print(f"Added Finnkode: {finncode}, Link: {link}, \n Name:{car_name} \n Price: {price} \n Spesifikasjoner:{combined_specs} \n Utstyr:{equipment_list} ") 
                    except Exception as e:
                        print(f"An error occurred while processing {finnkode}: {e}")
                else:
                    print(f"Finnkode {finnkode} already exists in the database.")
                 
            time.sleep(10)
    print(len(links), "Cars added.")
    