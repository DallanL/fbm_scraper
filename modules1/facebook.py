import pickle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import time
import re

def load_cookies(driver, cookies_file):
    with open(cookies_file, "rb") as file:
        cookies = pickle.load(file)
    for cookie in cookies:
        driver.add_cookie(cookie)

def fb_infinite_scroll(driver):
    SCROLL_PAUSE_TIME = 4
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        import datetime
        time_past = datetime.datetime.now()
        while (datetime.datetime.now() - time_past).seconds <=SCROLL_PAUSE_TIME:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def fb_get_listing_data(url, driver):
    #scrape description
    try:
        driver.get(url)
        time.sleep(2)
        #WebDriverWait(driver, 10).until(lambda driver: driver.execute_script('return document.readyState') == 'complete') #makes it go WAY faster... but might get your account banned for "going too fast" lol

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        description = soup.find('div', class_='xz9dl7a x4uap5 xsag5q8 xkhd6sd x126k92a').find('span').get_text(strip=True)
    except Exception as e:
        print(f"fb_get_listing_data - error opening {url}")
        print("Exception:", e)
        description = "empty"

    #scrape images?
    #return results
    if description == "":
        description = "empty"
    return description

def fb_scam_check(title, description):
    #check for websites
    sites_pattern = re.compile(r'website|cpucheap|cpubest|cpulot|lotcpu|dotcom|online shop', re.IGNORECASE)  
    #check for financing
    finance_pattern = re.compile(r'financ|payments|credit', re.IGNORECASE)
    #check for pay triple
    triple_pattern = re.compile(r'three times|ask me how', re.IGNORECASE)
    #check for common scam terms
    scam_pattern = re.compile(r'the item|cash\s?app only|only cash\s?app|shipping only|only ship', re.IGNORECASE)
    
    sites_match = sites_pattern.search(description)
    finance_match = finance_pattern.search(description)
    finance_title_match = finance_pattern.search(title)
    triple_match = triple_pattern.search(description)
    scam_match = scam_pattern.search(description)
    scam_title_match = scam_pattern.search(title)

    if sites_match:
        print(f"SCAM SITES - {title}")
        scam_check = "scam"
        return scam_check
    elif finance_match or finance_title_match:
        print(f"SCAM FINANCE - {title}")
        scam_check = "scam"
        return scam_check
    elif triple_match:
        print(f"SCAM TRIPLE - {title}")
        scam_check = "scam"
        return scam_check
    elif scam_match or scam_title_match:
        print(f"SCAM SCAM - {title}")
        scam_check = "scam"
        return scam_check
    else:
        return None

def fb_report_and_block(driver):
    #click triple dot menu
    try:
        menu_button = driver.find_element(By.CSS_SELECTOR, "div[aria-label='More Item Options']")
        menu_button.click()
        time.sleep(1)
    except Exception as e:
        print("cannot find the menu or error occurred:", e)
    time.sleep(1)
    #click report listing
    try:
        report_button = driver.find_element(By.XPATH, "//div[contains(@class, 'x1i10hfl') and @role='menuitem']//span[text()='Report listing']")
        report_button.click()
        time.sleep(1)
    except Exception as e:
        print("cannot find the report button or error occurred:", e)
        return
    time.sleep(1)
    #click scam
    try:
        scam_button = driver.find_element(By.XPATH, "//div[contains(@class, 'x1i10hfl x1qjc9v5 xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 x2lah0s xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1q0g3np x87ps6o x1lku1pv x1a2a7pz x1lq5wgf xgqcy7u x30kzoy x9jhf4c x1lliihq') and @role='button']//span[text()='Scam']")
        scam_button.click()
        time.sleep(1)
    except Exception as e:
        print("cannot find the scam option or error occurred:", e)
        return
    time.sleep(1)
    #click block
    try:
        block_button = driver.find_element(By.XPATH, "//div[contains(@class, 'x1i10hfl x1qjc9v5 xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 x2lah0s xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1q0g3np x87ps6o x1lku1pv x1a2a7pz x1lq5wgf xgqcy7u x30kzoy x9jhf4c x1lliihq') and @role='button']//span[contains(text(), 'Block')]")
        block_button.click()
        time.sleep(1)
    except Exception as e:
        print("cannot find the block option or error occurred:", e)
        return
    time.sleep(1)
    #click to confirm block
    try:
        block2_button = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Block']")
        block2_button.click()
        time.sleep(1)
    except Exception as e:
        print("cannot find the 2nd block option or error occurred:", e)
        return
    time.sleep(1)
    #click confirm block
    try:
        confirm_button = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Confirm']")
        confirm_button.click()
        time.sleep(1)
    except Exception as e:
        print("cannot find the confirm button or error occurred:", e)
        return
    time.sleep(1)
    #click done
    try:
        done_button = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Done']")
        done_button.click()
        time.sleep(1)
    except Exception as e:
        print("cannot find the done button or error occurred:", e)
        return
    return
