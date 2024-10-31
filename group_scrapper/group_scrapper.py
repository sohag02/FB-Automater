import logging
import random
import time
import re

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

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
import csv

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


def parse_group_info(info_string: str) -> dict:
    # Split the string by ' · ' to get each component
    parts = info_string.split(" · ")

    # Extract status directly
    status = parts[0]

    # Extract and convert members to an integer, removing 'K' or 'M' suffixes
    members_match = re.search(r"(\d+(\.\d+)?)([KM]?)", parts[1])
    if members_match:
        members = float(members_match.group(1))  # Extract the number part
        suffix = members_match.group(3)  # Extract the suffix (if any)
        if suffix == "K":
            members = int(members * 1_000)
        elif suffix == "M":
            members = int(members * 1_000_000)
        else:
            members = int(members)
    else:
        members = None

    # Extract and convert posts to an integer, removing '+' sign if present
    posts_match = re.search(r"(\d+)", parts[2])
    posts = int(posts_match.group(0)) if posts_match else None

    # Create the resulting dictionary
    result = {"status": status, "members": members, "posts": posts}

    return result


def scrape_groups(driver: Chrome):
    driver.get(f"https://www.facebook.com/search/groups?q={config.group_keyword}")
    wait_for_page_load(driver)
    unique_groups = set()

    logging.info("Scraping groups...")
    while config.group_count == 0 or len(unique_groups) < config.group_count:
        articles = driver.find_elements(
            By.XPATH,
            '//div[@role="article"]',
        )
        # groups = driver.find_elements(
        #     By.XPATH,
        #     '//div[@role="article"]//a[starts-with(@href, "https://www.facebook.com/groups/")]',
        # )
        for article in articles:
            try:
                group = article.find_element(
                    By.XPATH,
                    './/a[starts-with(@href, "https://www.facebook.com/groups/")]',
                )
                group_id = group.get_attribute("href").split("/")[-2]
                details = article.find_element(
                    By.XPATH,
                    './/span[contains(@class, "x1lliihq x6ikm8r x10wlt62 x1n2onr6")]',
                )
                # print(group_id)
                group_info = parse_group_info(details.text)
                # print(group_info)
                if group_id not in unique_groups:
                    if group_info["members"] < config.group_followers:
                        continue
                    if group_info["posts"] < config.group_posts:
                        continue
                    with open("groups.csv", "a", newline='') as f:
                        file = csv.writer(f)
                        # write row with id, name, status, members, posts
                        file.writerow(
                            [group_id, group_info["members"], group_info["posts"]]
                        )
                        # f.write(f"{group_id}\n")
                    unique_groups.add(group_id)
                    print("Scrapped Groups : ", len(unique_groups), end="\r")
            except Exception:
                continue
        scroll_down(driver)
        time.sleep(2)


def main():
    sessions = load_sessions(count=None)
    session = random.choice(sessions)
    logging.info(f"Scraping users using {session}")
    proxy = None
    if config.use_proxy:
        if config.rotating_proxies:
            proxy = extension
        else:
            proxy = proxies[0]
            proxies.pop(0)

    with setup_driver(session, config.headless, proxy=proxy) as driver:
        driver.get("https://www.facebook.com/")
        load_cookies(driver, f"sessions/{session}")
        verify_login(driver)
        scrape_groups(driver)


if __name__ == "__main__":
    main()
