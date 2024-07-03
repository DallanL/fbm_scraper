from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv
import os
import re
from modules1.cleanup import gpu_simplified
from modules1.sheets import get_price_thresholds,authenticate_google_sheets,write_to_google_sheets
from modules1.facebook import load_cookies,fb_get_listing_data,fb_scam_check,fb_report_and_block,fb_infinite_scroll
import psutil
import pickle

load_dotenv()
sheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')
api_key = os.getenv('GOOGLE_API_KEY')
driver_loc = os.getenv('DRIVER_LOC')
google_creds = os.getenv('GOOGLE_CREDS')
cookie_file = os.getenv('FB_COOKIE')
sheet_key = "1PegKY7IeELKeCivpI_CYbD368Y3cCXvWbDPEIW4jmhw" #jasril's pricing guide, used to get gpu price thresholds
chrome_bin = os.getenv('CHROME_BINARY')

client = authenticate_google_sheets(google_creds)

def kill_chrome_processes():
    for process in psutil.process_iter():
        try:
            if process.name() == "chrome.exe" or process.name() == "chromedriver.exe":
                process.kill()
        except psutil.NoSuchProcess:
            pass

def crawl_facebook_marketplace(city):
    min_price = 12
    #define list of GPUs to always check their descriptions for scams
    hot_gpus = ["RTX 3090", "RTX 4070", "RTX 4070 TI", "RTX 4070 SUPER", "RTX 4070 TI SUPER", "RTX 4080", "RTX 4080 SUPER", "RTX 4090"]
    # Setup headless Chrome
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920x1080")
    if chrome_bin:
        chrome_options.binary_location=chrome_bin
    
    # Block notifications
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    service = Service(driver_loc)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://www.facebook.com")
        load_cookies(driver, cookie_file)
        WebDriverWait(driver, 10).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')

        driver.refresh()
        WebDriverWait(driver, 10).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        price_thresholds = get_price_thresholds(client, sheet_key)
        
        results = []
        for city in cities:
            marketplace_url = f'https://www.facebook.com/marketplace/{city}/video-cards/?minPrice={min_price}'
            driver.get(marketplace_url)
            # Optionally wait for the page to load completely
            WebDriverWait(driver, 10).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')

            fb_infinite_scroll(driver)

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Scrape data
            listings = soup.find_all('div', class_='x9f619 x78zum5 x1r8uery xdt5ytf x1iyjqo2 xs83m0k x1e558r4 x150jy0e x1iorvi4 xjkvuk6 xnpuxes x291uyu x1uepa24')
            print(f"Found {len(listings)} listings")

            data = []
            for listing in listings:
                try:
                    #print(f'working on listing {listing}')
                    # Extract title
                    try:
                        title = listing.find('span', 'x1lliihq x6ikm8r x10wlt62 x1n2onr6').text
                    except Exception as e:
                    #    title = "Title not found"
                    #    print("Error finding title:", e)
                        continue
                    # Extract price
                    try:
                        price_text = listing.find('span', 'x193iq5w xeuugli x13faqbe x1vvkbs x10flsy6 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1tu3fi x3x7a5m x1lkfr7t x1lbecb7 x1s688f xzsf02u').text
                        price = float(price_text.replace('$', '').replace(',', ''))
                    except Exception as e:
                        price = None
                        print("Error finding price:", e)
                        continue
                # Extract location
                    try:
                        #location = listing.find('span', 'x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft x1j85h84').text #windows11
                        location = listing.find('span', 'x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft').text #linux
                        if location == "Ships to you":
                            continue
                    except Exception as e:
                        location = "Location not found"
                        continue
                    #    print("Error finding location:", e)
                    # Extract link
                    try:
                        link_tag = listing.find('a', class_='x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1sur9pj xkrqix3 x1lku1pv')['href']
                        if link_tag:
                            parsed_link = urlparse(link_tag)
                            base_link = parsed_link.path
                            link = urljoin("https://facebook.com", base_link)
                        else:
                            link = 'Link not found'
                            continue
                    except Exception as e:
                        link = "Link not found"
                        continue
                    #    print("Error finding link:", e)
                    # Extract image
                    #try:
                    #    image = listing.find('img', class_='xt7dq6l xl1xv1r x6ikm8r x10wlt62 xh8yej3')['src']
                    #except Exception as e:
                    #    image = "Image not found"
                    #    print("Error finding image:", e)

                    #if gpu_pattern.search(title):
                    try:
                        gpu = gpu_simplified(title, "0")
                    except Exception as e:
                        print(f"Error 141 failed to identify gpu: {title}")
                        print("Exception:", e)
                        continue

                    if gpu == "generic":
                        print(f'GENERIC - {title} - scan description here')
                        description = fb_get_listing_data(link, driver)
                        scam_check = fb_scam_check(title, description)
                        #print(scam_check)
                        if scam_check == "scam":
                            print(f"SCAM - {title}")
                            fb_report_and_block(driver)
                            continue
                        try:
                            gpu = gpu_simplified(description, "0")
                        except Exception as e:
                            print(f"Error 141 failed to identify gpu: {title}")
                            print("Exception:", e)
                            continue

                    #print(f"Checking if GPU: {gpu} is in price thresholds and price: {price} is <= {price_thresholds.get(gpu, 'N/A')}")
                    if gpu is None:
                        #print(f'{title} is not a recognized gpu - {gpu}')
                        continue
                    elif gpu == "old":
                        print(f'OLD - {title}')
                        continue
                    elif gpu == "tesla":
                        print(f'TESLA - {title}')
                        continue
                    elif gpu in price_thresholds and price is not None:
                        threshold_price = price_thresholds[gpu]
                        print(f"PRICE CHECK: {gpu} is in price thresholds and price: {price} is <= {threshold_price}")
                        if price <= threshold_price:
                            if gpu in hot_gpus:
                                description = fb_get_listing_data(link, driver)
                                print(f"Scam check: {title} , description: {description}")
                                scam_check = fb_scam_check(title, description)
                                #print(scam_check)
                                if scam_check == "scam":
                                    print(f"SCAM - {title}")
                                    fb_report_and_block(driver)
                                    continue
                                elif price <= 0.8 * threshold_price:
                                    title += "*SUSPICIOUS*"
                            if gpu not in hot_gpus and price <= 0.5 * threshold_price:
                                description = fb_get_listing_data(link, driver)
                                print(f"Scam check: {title} , description: {description}")
                                scam_check = fb_scam_check(title, description)
                                #print(scam_check)
                                if scam_check == "scam":
                                    print(f"SCAM - {title}")
                                    fb_report_and_block(driver)
                                    continue

                            data.append({
                                "gpu": gpu,
                                "title": title,
                                "price": price,
                                "location": location,
                                "link": link
                                #,"image": image
                            })
                        #else: #if price is over the threshold?
                    else:
                        #print(f'listing: {title} is not a recognized GPU')
                        continue
                        #    print(f'{gpu} price of {price} is higher than {price_thresholds[gpu]}')
            #print(f"Scraped data: {title}, {price}, {location}, {link}, {image}")
            #break
                except Exception as e:
                    print(f"Error 174 scraping listing: {listing}")
                    print("Exception:", e)
                    #break
                    continue
            results.extend(data)
            print(f"Deals in {city}:", len(data))
    finally:
        driver.quit() #close the browser
    print(f"Total Deals:", len(results))
    return results

cities = {
        "nyc",
        "la",
        "vegas",
        "chicago",
        "houston",
        "sanantonio",
        "miami",
        "orlando",
        "sandiego",
        "arlington",
        "baltimore",
        "cincinati",
        "denver",
        "fortworth",
        "jacksonville",
        "memphis",
        "nashville",
        "philly",
        "portland",
        "sanjose",
        "tucson",
        "atlanta",
        "boston",
        "columbus",
        "detroit",
        "honolulu",
        "kansascity",
        "neworleans",
        "phoenix",
        "seattle",
        "dc",
        "milwaukee",
        "sac",
        "austin",
        "charlotte",
        "dallas",
        "elpaso",
        "indianapolis",
        "louisville",
        "minneapolis",
        "oklahoma",
        "pittsburgh",
        "sanfrancisco",
        "tampa"
        }

listings = crawl_facebook_marketplace(cities)

if len(listings) > 0:
    # Write data to Google Sheets
    write_to_google_sheets(client, sheet_id, "Sheet1", listings)
else:
    print("No Listings to process")

# Kill all leftover Chrome processes
kill_chrome_processes()
