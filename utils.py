import json
import pickle
import logging
from contextlib import contextmanager
import random

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Set up logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_cookies(driver, cookies_file):
    """Load cookies from a file and add them to the driver."""
    try:
        with open(cookies_file, "rb") as file:
            cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()
        logging.info(f"Logged in successfully with {cookies_file.replace('sessions/', '')}")
    except Exception as e:
        logging.error(f"Failed to load cookies: {e}")

@contextmanager
def setup_driver(session_name, headless=True):
    """Set up the Selenium WebDriver with options."""
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument('--log-level=3')  # Suppress logs
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--mute-audio")

    driver = webdriver.Chrome(options=chrome_options)
    driver.session_name = session_name
    
    try:
        logging.info(f"Driver initialized for session: {session_name}")
        yield driver  # This allows the driver to be used inside the 'with' block
    finally:
        driver.quit()
        logging.info(f"Driver closed for session: {session_name}")

def get_comments():
    """Retrieve comments from a JSON file."""
    try:
        with open("comments.json", "r") as file:
            comments = json.load(file)
        logging.info("Comments loaded successfully.")
        return comments['comments']
    except Exception as e:
        logging.error(f"Failed to load comments: {e}")
        return []

def like(driver):
    """Click the like button on a post."""
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Like"]'))
        ).click()
        logging.info(f"Post liked with {driver.session_name}")
    except:
        logging.info(f"Post already liked with {driver.session_name}")

def comment(driver, text):
    """Leave a comment on a post."""
    try:
        # Open comment box
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Comment"]'))
        ).click()
        # Write comment
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Write a comment…"]'))
        ).send_keys(text)
        # Send
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Comment"]'))
        ).click()
        logging.info(f'Commented with {driver.session_name}: "{text}"')
    except Exception as e:
        logging.error(f"Failed to comment with {driver.session_name}")

def verify_login(driver):
    try:
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Your profile"]'))
        ).click()
    except:
        logging.error(f"There is an issue with the account : {driver.session_name}. Skipping...")
        driver.quit()

def getImage(size='1080'):
    url = f'https://picsum.photos/{size}'
    response = requests.get(url)
    # random name
    fileName = f'post_{random.randint(0, 1000)}.jpg'
    # Download image
    with open(fileName, 'wb') as file:
        file.write(response.content)
    return fileName

def remove_non_bmp_characters(text):
    return ''.join(char for char in text if ord(char) <= 0xFFFF)

def getCaption():
    with open('captions.json', encoding='utf-8') as f:
        data = json.load(f)
        caption = random.choice(data['captions'])
        return remove_non_bmp_characters(caption + " ")

def getBio():
    with open('bio.json', encoding='utf-8') as f:
        data = json.load(f)
        bio = random.choice(data['bio'])
        return remove_non_bmp_characters(bio + " ")