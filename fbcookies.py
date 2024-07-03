import pickle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from dotenv import load_dotenv
import os

load_dotenv()
driver_loc = os.getenv('DRIVER_LOC')


def save_facebook_cookies():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.binary_location='/home/dallanl00mis/Downloads/chrome-linux64/chrome'

    service = Service(driver_loc)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get("https://www.facebook.com")
    time.sleep(20)  # Adjust time as needed to log in manually

    # Save cookies to a file
    cookies = driver.get_cookies()
    with open("facebook_cookies.pkl", "wb") as file:
        pickle.dump(cookies, file)

    driver.quit()

# Run this function to save the cookies after logging in manually
save_facebook_cookies()

