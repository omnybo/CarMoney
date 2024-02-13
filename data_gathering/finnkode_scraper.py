from selenium import webdriver
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display
import time
#import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options
import os
import requests
import sqlite3
import json
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException




class FinnkodeScraper:
    def __init__(self, url):
        self.url = url
        self.display = Display(visible=0, size=(800, 600))  # Initialize the virtual display
        self.display.start()  # Start the virtual display
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
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

        # Extract data: finnkode, link, car name, and price

        articles = self.driver.find_elements(By.XPATH, "//article[contains(@class, 'sf-search-ad')]")
        for idx, article in enumerate(articles, start=1):
            link_element = article.find_element(By.XPATH, ".//a[contains(@href, 'finnkode=')]")
            href = link_element.get_attribute("href")
            finnkode = href.split("finnkode=")[1].split("&")[0]
            
            # Extract car name
            car_name_element = article.find_element(By.XPATH, ".//h2/a")
            car_name = car_name_element.text.strip()
            # Extracting price using the provided XPath structure, adjusted for iteration
            try:
                if idx == 1:
                    price_xpath = f"/html/body/div[2]/main/div/div[2]/section[2]/div[3]/article[{idx}]/div[3]/div[4]/span[3]"
                else:
                    price_xpath = f"/html/body/div[2]/main/div/div[2]/section[2]/div[3]/article[{idx}]/div[3]/div[3]/span[3]"
                price_element = self.driver.find_element(By.XPATH, price_xpath)
                price = price_element.text.strip()
            except:
                price = None  # If the price element is not found, set price to None


            data.append((finnkode, href, car_name, price))
        return data

    def extract_all_info(self):
        # Navigate to the provided URL
        self.driver.get(self.url)
        time.sleep(2)  # ensure all elements are loaded, might require fine-tuning

        # Initialize containers for the information to be scraped
        specifications = {}
        description = ""
        equipment_list = []
        name = ""
        price = ""

        try:
            # Find the <dl> element by its class.
            dl_element = self.driver.find_element(By.CSS_SELECTOR, "dl.list-descriptive.u-col-count2.u-col-count3from990")

            # Find all <div> elements within the <dl> element.
            div_elements = dl_element.find_elements(By.XPATH, ".//div")

            # Loop through each <div> element and extract the text of <dt> and <dd> elements.
            for div in div_elements:
                dt = div.find_element(By.TAG_NAME, "dt").text
                dd = div.find_element(By.TAG_NAME, "dd").text
                specifications[dt] = dd
        except Exception as e:
            print(f"An error occurred while extracting specifications: {e}")

        try:
            # Extracting description
            section = self.driver.find_element(By.CSS_SELECTOR, "section.panel.u-mt32.import-decoration")
        
            # Within that section, find the 'Beskrivelse' element and the subsequent <p> element.
            description_container = section.find_element(By.XPATH, ".//h2[contains(text(),'Beskrivelse')]/following-sibling::p")
            description = description_container.get_attribute("innerHTML")
        except Exception as e:
            print(f"An error occurred while extracting description: {e}")

        try:
            # Extracting equipment list
            # Find the ul element containing the items
            ul_element = self.driver.find_element(By.CSS_SELECTOR, "section.panel.u-mt32 ul.list.u-col-count2.u-col-count3from990")

            # Get all the li elements in the list
            # Change from find_element to find_elements to get a list of elements
            li_elements = ul_element.find_elements(By.TAG_NAME, "li")

            # Extract the text from each li element
            equipment_list = [li.text for li in li_elements]
        except Exception as e:
            print(f"An error occurred while extracting equipment list: {e}")
        try:
            # Extracting name
            name_element = self.driver.find_element(By.CSS_SELECTOR, "div.panel h1.u-t2.u-word-break")
            name = name_element.text
        except Exception as e:
            print(f"An error occurred while extracting name: {e}")

        try:
            # Extracting price
            price_element = self.driver.find_element(By.CSS_SELECTOR, "div.flex-wrapper__unit span.u-t3")
            price = price_element.text
        except Exception as e:
            print(f"An error occurred while extracting price: {e}")
        return {
            "name": name,
            "price": price,
            "specifications": specifications,
            "description": description,
            "equipment_list": equipment_list
        }
    
    def extract_all_info_and_images(self):
        # Navigate to the provided URL
        self.driver.get(self.url)
        try:
            dl_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "dl.list-descriptive.u-col-count2.u-col-count3from990"))
            )
        except TimeoutException:
            print("The dl element was not found within the given time frame.")
            #return None
        time.sleep(3)  # ensure all elements are loaded, might require fine-tuning

        # Initialize containers for the information to be scraped
        specifications = {}
        description = ""
        equipment_list = []
        img_links = []
        name = ""
        price = ""
        
        try:
            # Find the <dl> element by its class.
            dl_element = self.driver.find_element(By.CSS_SELECTOR, "dl.list-descriptive.u-col-count2.u-col-count3from990")

            # Find all <div> elements within the <dl> element.
            div_elements = dl_element.find_elements(By.XPATH, ".//div")

            # Loop through each <div> element and extract the text of <dt> and <dd> elements.
            for div in div_elements:
                dt = div.find_element(By.TAG_NAME, "dt").text
                dd = div.find_element(By.TAG_NAME, "dd").text
                specifications[dt] = dd
        except Exception as e:
            print(f"An error occurred while extracting specifications: {e}")

        try:
            # Extracting description
            section = self.driver.find_element(By.CSS_SELECTOR, "section.panel.u-mt32.import-decoration")

            # Within that section, find the 'Beskrivelse' element.
            beskrivelse_element = section.find_element(By.XPATH, ".//h2[contains(text(),'Beskrivelse')]")
            
            # Initialize the description as an empty list.
            descriptions = []

            # Loop through all direct <p> siblings after 'Beskrivelse'
            next_sibling = beskrivelse_element
            while True:
                try:
                    # Try finding the next <p> sibling.
                    next_sibling = next_sibling.find_element(By.XPATH, "following-sibling::p[1]")
                    

                    # Otherwise, add the text of the <p> element to our list.
                    descriptions.append(next_sibling.get_attribute("innerHTML"))
                except NoSuchElementException:
                    # If no more <p> siblings are found, break out of the loop.
                    break

                # Combine all descriptions into a single string.
                description = ' '.join(descriptions)

        except Exception as e:
            print(f"An error occurred while extracting description: {e}")

        try:
            # Extracting equipment list
            # Find the ul element containing the items
            ul_element = self.driver.find_element(By.CSS_SELECTOR, "section.panel.u-mt32 ul.list.u-col-count2.u-col-count3from990")

            # Get all the li elements in the list
            # Change from find_element to find_elements to get a list of elements
            li_elements = ul_element.find_elements(By.TAG_NAME, "li")

            # Extract the text from each li element
            equipment_list = [li.text for li in li_elements]
        except Exception as e:
            #print(f"An error occurred while extracting equipment list: {e}")
            print("No equipment list found.")
            
        try:  
            imgs = self.driver.find_elements(By.XPATH, "//section[contains(@class, 'panel mt-0')]//img")
            
            for img in imgs:
                src = img.get_attribute('src')
                if src:
                    img_links.append(src)
                else:
                    src = img.get_attribute('data-src')
                    if src:
                        # 'srcset' could contain multiple URLs - here we're taking the first one
                        img_links.append(src)
        except Exception as e:
            print(f"An error occurred while extracting images: {e}")

        # Extracting Modellår
        try:
            modellår_element = self.driver.find_element(By.XPATH, "//div[contains(text(),'Modellår')]/following-sibling::div")
            specifications["modellår"] = modellår_element.text.strip()
        except Exception:
            specifications["modellår"] = "NOT FOUND"

        # Extracting Kilometer
        try:
            kilometer_element = self.driver.find_element(By.XPATH, "//div[contains(text(),'Kilometer')]/following-sibling::div")
            specifications["kilometer"] = kilometer_element.text.strip()
        except Exception:
            specifications["kilometer"] = "NOT FOUND"

        # Extracting Girkasse
        try:
            girkasse_element = self.driver.find_element(By.XPATH, "//div[contains(text(),'Girkasse')]/following-sibling::div")
            specifications["girkasse"] = girkasse_element.text.strip()
        except Exception:
            specifications["girkasse"] = "NOT FOUND"

        # Extracting Drivstoff
        try:
            drivstoff_element = self.driver.find_element(By.XPATH, "//div[contains(text(),'Drivstoff')]/following-sibling::div")
            specifications["drivstoff"] = drivstoff_element.text.strip()
        except Exception:
            specifications["drivstoff"] = "NOT FOUND"
        try:
            # Extracting name
            name_element = self.driver.find_element(By.CSS_SELECTOR, "div.panel h1.u-t2.u-word-break")
            name = name_element.text
        except Exception as e:
            print(f"An error occurred while extracting name: {e}")

        try:
            # Extracting price
            price_element = self.driver.find_element(By.CSS_SELECTOR, "div.flex-wrapper__unit span.u-t3")
            price = price_element.text
        except Exception as e:
            print(f"An error occurred while extracting price: {e}")
        return {
            "name": name,
            "price": price,
            "specifications": specifications,
            "description": description,
            "equipment_list": equipment_list,
            "image_links": img_links
        }
        
    def save_images(self, image_links, destination_folder):
        if not image_links:  # Check if image_links list is empty
            print("No image links provided for download.")
            return
        
        if not os.path.exists(destination_folder):
            os.mkdir(destination_folder)

        for idx, img_url in enumerate(image_links):
            time.sleep(0.5)
            response = requests.get(img_url)
            if response.status_code == 200:
                filename = os.path.join(destination_folder, f"image_{idx}.jpg")
                with open(filename, 'wb') as file:
                    file.write(response.content)
            else:
                print(f"Failed to download {img_url}")
        
    def close(self):
        self.driver.close()
        self.display.stop()

def insert_car(conn, finnkode, car_name, link, price, pictures=None):
    sql = 'INSERT INTO Car(Finnkode, car_name, Link, Price, Pictures) VALUES(?,?,?,?,?)'
    cur = conn.cursor()
    cur.execute(sql, (finnkode, car_name, link, price, pictures))
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
    all_finnkodes_links = []
    base_folder = "images/"
    if not os.path.exists(base_folder):
            os.mkdir(base_folder)
    counter = 0
    change = 5000
    for x in range(0, 1500000, change):
        for i in range(50):
            URL = "https://www.finn.no/car/used/search.html?page="+str(i+1)+"&price_from="+str(x+1)+"&price_to="+str(x+change)+"&sales_form=1&sort=PUBLISHED_DESC"
            #URL = "https://www.finn.no/car/used/search.html?page="+str(i+1)+"&sales_form=1"
            print('Scraping page from: ' +URL)
            scraper = FinnkodeScraper(URL)
            data = scraper.get_finnkodes_links_and_prices()

            if not data or len(data) <= 1:
                break
            #print(data)
            scraper.close()
            # add the newly scraped finnkodes_links to the full list
            all_finnkodes_links.extend(data)
            for finnkode, link, car_name, price in data:
                database = "cars.db" # replace with your actual SQLite database path
                # create a database connection
                conn = sqlite3.connect(database)
                cursor = conn.cursor()
                if element_exists(cursor, 'Car', 'Finnkode', finnkode):
                    print("Element exists")
                else:
                    try:
                        print('Adding car with finnkode: ' +finnkode)
                        if price is None:
                            continue


                        car_scraper = FinnkodeScraper(link)
                        car_info = car_scraper.extract_all_info_and_images()
                        dest_folder = base_folder + str(finnkode)
                        car_scraper.save_images(car_info['image_links'], destination_folder=dest_folder)
                        car_scraper.close()


                        with conn:
                            insert_car(conn, finnkode, car_name, link, price, dest_folder)
                            insert_description(conn, finnkode, car_info['description'])
                            insert_specifications(conn, finnkode, car_info['specifications'])
                            #print(car_info['specifications'])
                            insert_equipment(conn, finnkode, car_info['equipment_list'])
                        print(f"Added Finnkode: {finnkode}, Link: {link}, Price: {price}")
                    except Exception as e:
                        print(f"An error occurred while scraping {finnkode}: {e}")

            # Wait for the page to load
            time.sleep(10)
    print(len(all_finnkodes_links))

