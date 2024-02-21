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
   
    def extract_finnkode(self):
        # Extract the Finnkode from the URL
        finnkode = self.url.split('finnkode=')[-1].split('&')[0]
        return finnkode
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
    def extract_price(self):
        try:
            price_section = scraper.driver.find_element(By.CSS_SELECTOR, "section.panel.u-mt32:not(.import-decoration) .flex-wrapper .flex-wrapper__unit .u-t3")
            print("DEBUG: Price element HTML:", price_section.get_attribute('outerHTML'))  # This will print the HTML of the price element
            price = scraper.driver.execute_script('return arguments[0].textContent;', price_section)
            #exclude chars (kr)
            numeric_price = re.sub("[^\d]", "", price)  # This removes all non-digit charactersprint("Extracted Numeric Price:", numeric_price)
        except Exception as e:
            print(f"An error occurred while trying to extract the price: {e}")

        return numeric_price

           
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
    
    def close(self):
        self.driver.close()

if __name__ == "__main__":
    # Example URL
    car_url = "https://www.finn.no/car/used/ad.html?finnkode=340869847"
    
    # Create an instance of the scraper
    scraper = FinnkodeScraper(car_url)
    
    # Extract and print information
    finnkode = scraper.extract_finnkode()
    description = scraper.extract_description()
    numeric_price = scraper.extract_price()
    name = scraper.extract_model_name()
    specs = scraper.extract_car_specs()
    
    #print(specs, "\n",name, "\n pris:",numeric_price,  "\n finnkode:" ,finnkode, "\n Description", description)
    
    equipment_list = scraper.extract_equipment()
    print(f"---- Car Info ---- \n Name: {name} \n Pris: {numeric_price} \n Spesifikasjoner: {specs} \n Utstyr: {equipment_list} \n Beskrivelse: {description}")
    
    # Close the browser after scraping is done
    
    scraper.close()
