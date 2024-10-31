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
)
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

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

POST_DIR = os.path.join(os.getcwd(), "group_poster", "group_posts")
CAPTION_FILE = os.path.join(os.getcwd(), "group_poster", "captions.json")

def get_caption():
    with open(CAPTION_FILE, encoding="utf-8") as f:
        data = json.load(f)
        return random.choice(data["captions"])
    
def get_post():
    posts = os.listdir(POST_DIR)
    if posts:
        return random.choice(posts)
    else:
        return None
    
def load_groups():
    df = pd.read_csv("groups.csv")
    return df['group_id'].tolist()

def post_in_group(driver: Chrome, group_id: str):
    try:
        driver.get(f"https://www.facebook.com/groups/{group_id}")
        wait_for_page_load(driver)
        # Open post box
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//span[contains(text(), \"Write something\")]"))
        ).click()

        caption = get_caption()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[aria-label="Create a public post…"]')
            )
        ).send_keys(caption)

        post = get_post()

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[aria-label="Photo/video"]')
            )
        ).click()

        file_input = driver.find_element(By.XPATH, "//input[@type='file']")
        print(file_input.get_attribute("accept"))
        print(file_input.get_attribute("class"))
        driver.execute_script("arguments[0].style.display = 'block';", file_input)
        print("exe")
        time.sleep(5)
        file_input.send_keys(os.path.join(POST_DIR, post))
        print("keys")
        time.sleep(5)

        # WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable(
        #         (By.CSS_SELECTOR, '[aria-label="Post"]')
        #     )
        # ).click()
        logging.info(f"Successfully posted in {group_id} with {driver.session_name}")
        time.sleep(5)
        return True
    except Exception:
        # raise
        logging.error(f"Failed to post in {group_id} with {driver.session_name}")
        return False

def create_csv_log():
    today = datetime.now().date().strftime("%d-%m-%Y")
    filename = f"group_poster/{today}.csv"

    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("group_id,session_name\n")

    return filename


def main():
    sessions = load_sessions(config.sessions)
    groups = load_groups()

    file = create_csv_log()

    for session in sessions:
        proxy = None
        if config.use_proxy:
            if config.rotating_proxies:
                proxy = extension
            else:
                proxy = proxies[0]
                proxies.pop(0)
        with setup_driver(session, headless=config.headless, proxy=proxy) as driver:
            driver.get("https://www.facebook.com/")
            load_cookies(driver, f"sessions/{session}")
            verify_login(driver)
            for _ in range(config.post_per_session):
                group_id = groups[0]
                groups.pop(0)
                if res := post_in_group(driver, group_id):
                    with open(file, "a") as f:
                        writer = csv.writer(f)
                        writer.writerow([group_id, session])
                time.sleep(config.delay)
if __name__ == "__main__":
    main()