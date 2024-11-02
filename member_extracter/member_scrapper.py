import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from main import load_sessions
import logging
from search import scroll_down
from utils import (
    load_cookies,
    setup_driver,
    get_proxies,
    verify_login,
    wait_for_page_load,
)
from config import Config
from proxy import check_proxies
from proxy_extension import create_proxy_auth_extension

import pandas as pd

from utils import extract_user_id

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


def scroll_page(driver: webdriver.Chrome):
    # Initial page height
    last_height = driver.execute_script("return document.body.scrollHeight")

    # Try scrolling down
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Wait for page to load

    # New page height after scrolling
    new_height = driver.execute_script("return document.body.scrollHeight")

    # Check if page height has changed
    if last_height == new_height:
        print("Page is not scrollable. Exiting.")
        # driver.quit()
        return False
    else:
        print("Page is scrollable.")
        return True

def scrape_members(session_file, username):
    proxy = None
    if config.use_proxy:
        if config.rotating_proxies:
            proxy = extension
        else:
            proxy = proxies[0]
            proxies.pop(0)
    with setup_driver(
        headless=config.headless, session_name=session_file, proxy=proxy
    ) as driver:
        driver.get("https://www.facebook.com/")
        load_cookies(driver, f"sessions/{session_file}")

        res = verify_login(driver)
        if not res:
            return
        driver.get(f"https://www.facebook.com/groups/{username}/members")
        wait_for_page_load(driver)
        time.sleep(5)

        logging.info("Scraping members...")
        # Initialize an empty set to store unique member URLs
        unique_members = set()

        with open(f"{username}.csv", "w") as f:
            pass

        # scroll_check = 0

        while True:
            try:
                # Find all member elements on the page
                members = driver.find_elements(
                    By.XPATH,
                    '//div[@role="listitem"]//a[starts-with(@href, "/groups/")]',
                )

                # Process each member element
                for member in members:
                    member_url = member.get_attribute("href")
                    member_id = extract_user_id(member_url)
                    # member_name = driver.execute_script("return arguments[0].innerText;", member)
                    if member_id not in unique_members:
                        unique_members.add(member_id)  # Add to set to keep track
                        print("Scrapped Members : ", len(unique_members), end="\r")
                        df = pd.DataFrame({"id": [member_id]})
                        df.to_csv(
                            f"{username}.csv",
                            mode="a",
                            index=False,
                            header=False,
                        )
                # Scroll down
                scroll_down(driver)
                time.sleep(2)

                if config.member_count and len(unique_members) >= config.member_count:
                    break

            except Exception as e:
                print(e)
                break

        logging.info(f"Total Members scraped: {len(unique_members)}")
        logging.info(f"Saved in {username}.csv")

def load_groups():
    df = pd.read_csv(config.group_csv_file, header=None)  # Load CSV without headers
    if df.shape[0] > 0:  # Check if the DataFrame is not empty
        # Check if the first row is a header (assuming headers are strings)
        if not df[0].apply(lambda x: isinstance(x, str)).all():
            return df[0].tolist()  # Return the first column as a list
        else:
            return df.iloc[1:, 0].tolist()  # Exclude the header row and return the first column as a list
    return []  # Return an empty list if the DataFrame is empty


if __name__ == "__main__":
    sessions = load_sessions()
    session = random.choice(sessions)

    groups = load_groups()
    if not groups:
        logging.error("No Groups Found")
        exit()

    for group in groups:
        scrape_members(session, group)
