import logging
import random
import time

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
from utils import extract_facebook_id

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


def scrape_users(driver: Chrome):
    driver.get(
        f"https://www.facebook.com/search/people?q={config.keyword} {config.location}"
    )
    wait_for_page_load(driver)
    unique_users = set()

    logging.info("Scraping users...")
    while len(unique_users) < config.user_count:
        users = driver.find_elements(
            By.XPATH,
            '//div[@role="article"]//a[starts-with(@href, "https://www.facebook.com/profile.php?id=")]',
        )
        for user in users:
            user_id = extract_facebook_id(user.get_attribute("href"))
            if user_id not in unique_users:
                print(user_id)
                with open("users.csv", "a") as f:
                    f.write(f"{user_id}\n")
                unique_users.add(user_id)
        print("Scrapped Users : ", len(unique_users), end="\r")
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
        scrape_users(driver)


if __name__ == "__main__":
    main()
