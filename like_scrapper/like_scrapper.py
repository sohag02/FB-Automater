import csv
import logging
import random
import time
import os
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
import json

from config import Config
from main import load_sessions
from proxy import check_proxies
from proxy_extension import create_proxy_auth_extension
from search import scroll_down
from utils import (
    get_proxies,
    load_cookies,
    setup_driver,
    verify_login,
    wait_for_page_load,
    extract_facebook_id,
)
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

import time
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains

from urllib.parse import urlparse

config = Config()

logging.getLogger("selenium").setLevel(logging.ERROR)

if config.use_proxy:
    if config.rotating_proxies:
        extension = create_proxy_auth_extension(
            config.host,
            config.port,
            config.proxy_username,
            config.proxy_password,
            "internal",
        )
        # proxy = None
    else:
        check_proxies(config.proxy_file)

proxies = []
if config.use_proxy and not config.rotating_proxies:
    proxies = get_proxies()

def scroll_modal(driver: WebDriver, modal: WebElement, increment: int = 100, delay: float = 0.2) -> bool:
    # Get the modal height
    modal_height = driver.execute_script("return arguments[0].scrollHeight;", modal)
    
    # Get the current scroll position
    current_scroll = 0
    
    # Scroll the modal in 100px increments
    while current_scroll < modal_height:
        actions = ActionChains(driver)
        actions.move_to_element(modal).scroll_by_amount(0, 300).perform()
        current_scroll += 300
        
        # Check if we've reached the bottom of the modal
        if driver.execute_script("return arguments[0].scrollTop + arguments[0].clientHeight >= arguments[0].scrollHeight;", modal):
            return False
    
    return True

def extract_username(url: str) -> str:
    # Parse the URL path
    path = urlparse(url).path
    
    # Split the path by '/' and return the last non-empty part as username
    parts = path.split('/')
    for part in reversed(parts):
        if part:
            return part.split('?')[0]  # Remove any query parameters
    
    return None

def like_scrapper(driver: Chrome, url):
    driver.get(url)
    wait_for_page_load(driver)
    logging.info("Scraping likes...")
    post_count = 0
    users_set = set()
    while post_count < config.post_range:
        try:
            print('getting posts')
            posts = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//div[starts-with(@aria-label, "Like:")]')
                )
            )
            for post in posts:
                print('processing post')
                driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", post)
                post.click()
                time.sleep(2)
                while True:
                    
                    users = driver.find_elements(
                        By.XPATH,
                        '//a[starts-with(@attributionsrc, "/privacy_sandbox/comet/register/source/")]',
                    )
                    for user in users:
                        user_link = user.get_attribute("href")
                        if 'id' in user_link:
                            user_id = extract_facebook_id(user_link)
                        else:
                            user_id = extract_username(user_link)
                            if user_id not in users_set:
                                users_set.add(user_id)
                                with open('users.csv', 'a', newline='') as csvfile:
                                    writer = csv.writer(csvfile)
                                    writer.writerow([user_id])
                                print(f'Scrapped Users : {len(users_set)}', end='\r')
                    
                    res = scroll_modal(driver, post)
                    if not res:
                        break
                    
                # close btn
                driver.find_element(By.XPATH, '//div[@aria-label="Close"]').click()
                time.sleep(2)

            scroll_down(driver, amt=2000)
        except Exception as e:
            print('error')
            print(e)
            continue
                

def main():
    sessions = load_sessions(config.sessions)

    session = random.choice(sessions)
    with setup_driver(session, headless=config.headless) as driver:
        driver.get("https://www.facebook.com/")
        load_cookies(driver, f"sessions/{session}")
        verify_login(driver)

        like_scrapper(driver, config.url)

if __name__ == "__main__":
    main()