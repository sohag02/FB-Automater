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
from selenium.webdriver.common.action_chains import ActionChains

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
CAPTION_FILE = os.path.join(os.getcwd(), "group_poster", "captions.txt")


def get_caption():
    with open(CAPTION_FILE, encoding="utf-8") as f:
        data = f.readlines()
    return random.choice(data).strip()


def get_post():
    return random.choice(posts) if (posts := os.listdir(POST_DIR)) else None


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

        input_box = None
        anonymous_allowed = False
        final_btn_selector = 'Post'
        # anonymous post
        if config.anonymous:
            try:
                WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR,
                         '[aria-label="Anonymous post toggle"]')
                    )
                ).click()
                WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, '[aria-label="Got it"]')
                    )
                ).click()

                input_box = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR,
                         '[aria-label="Submit an anonymous post…"]')
                    )
                )
                anonymous_allowed = True
                final_btn_selector = 'Submit'
            except:
                pass

        caption = get_caption()
        if not input_box:
            input_box = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '[aria-label="Create a public post…"]')
                )
            )

        input_box.send_keys(caption)

        post = get_post()

        upload_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[aria-label="Photo/video"]')
            )
        )
        if not anonymous_allowed:
            upload_btn.click()

        file_input = driver.find_element(By.XPATH, '//div[@role="dialog"]//input[@type="file"]')

        # Make file input visible
        driver.execute_script("""
            arguments[0].style = {};
            arguments[0].style.display = 'block';
            arguments[0].style.visibility = 'visible';
            arguments[0].style.opacity = '1';
            arguments[0].style.height = '100px';
            arguments[0].style.width = '100px';
            arguments[0].style.position = 'fixed';
            arguments[0].style.top = '0';
            arguments[0].style.left = '0';
            arguments[0].style.zIndex = '9999999';
            arguments[0].style.border = '5px solid red';
            arguments[0].style.backgroundColor = '#ffffff';
        """, file_input)

        # Prepare absolute file path
        path:str = os.path.abspath(os.path.join(POST_DIR, post))

        file_input.send_keys(path)
        file_input = driver.find_element(By.XPATH, "//input[@type='file']")


        post_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, f'//div[@role="dialog"]//div[@aria-label="{final_btn_selector}" and @role="button"]')
            )
        )
        time.sleep(5)
        actions = ActionChains(driver)
        # driver.execute_script("arguments[0].style.border = '5px solid red';", post_btn)
        actions.move_to_element(post_btn).click().perform()
        # driver.execute_script("arguments[0].click();", post_btn)
        # post_btn.click()
        logging.info(f"Successfully posted in {group_id} with {driver.session_name}")
        time.sleep(10)
        return True
    except Exception:
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
            res = verify_login(driver)
            if not res:
                continue
            for _ in range(config.post_per_session):
                group_id = groups[0]
                groups.pop(0)
                if res := post_in_group(driver, group_id):
                    with open(file, "a", newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([group_id, session])
                time.sleep(config.delay)


if __name__ == "__main__":
    main()
