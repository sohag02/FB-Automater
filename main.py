import csv
import logging
import multiprocessing
import os
import random
import time
from datetime import datetime
from multiprocessing import Pool

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import Config
from live import run_facebook_instance
from post import post
from utils import comment, get_comments, get_proxies, like, load_cookies, setup_driver, getBio, verify_login
from db import update_user_profile, get_user_profile, insert_user_profile
from fbProfile import setProfile
from friend import getFriends, accept_friend_requests

from proxy import check_proxies
from proxy_extension import create_proxy_auth_extension

logging.getLogger('selenium').setLevel(logging.ERROR)

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s - %(levelname)s - %(message)s')

config = Config()

if config.use_proxy:
    if config.rotating_proxies:
        extension = create_proxy_auth_extension(
            config.host, config.port, config.proxy_username, config.proxy_password, "internal")
        # proxy = None
    else:
        check_proxies(config.proxy_file)

proxies = []
if config.use_proxy and not config.rotating_proxies:
    proxies = get_proxies()


def load_sessions():
    if not os.path.exists("sessions"):
        logging.error("No Sessions Found")
        exit()

    if sessions := os.listdir("sessions"):
        return sessions[:config.accounts]
    logging.error("No Sessions Found")
    exit()


session_files = load_sessions()

comment_list = get_comments()

like_count = 0
comment_count = 0


def profile_status(session_name):
    if user := get_user_profile(session_name):
        return user.profile_setup
    insert_user_profile(session_name, datetime.now().date(), False)
    return False


def post_status(session_name):
    logging.info(f"Checking Post Status for {session_name}")
    if user := get_user_profile(session_name):
        date = user.last_post_date
        delta = datetime.now().date() - date
        return delta.days >= config.post_interval
    else:
        insert_user_profile(session_name, datetime.now().date(), False)
        return False


def navigate_to_reels(driver, profile_url):
    logging.info("Looking for Reels...")
    driver.get(profile_url)
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(3)


def watch_reels_from_link(link, watch_time, session_name, likes=None, comments=None):
    global like_count, comment_count
    proxy = None
    if config.use_proxy:
        if config.rotating_proxies:
            proxy = extension
        else:
            proxy = proxies[0]
            proxies.pop(0)
    with setup_driver(session_name, headless=config.headless, proxy=proxy) as driver:
        driver.get('https://www.facebook.com/')
        load_cookies(driver, f'sessions/{session_name}')

        verify_login(driver)

        if post_status(session_name):
            post(driver)

        if not profile_status(session_name):
            bio = getBio()
            setProfile(driver, bio)

        getFriends(driver)
        accept_friend_requests(driver)

        logging.info(f"Watching Reel: {link}")
        driver.get(link)
        time.sleep(5)

        if likes and likes > like_count:
            like(driver)
            like_count += 1
        if comments and comments > comment_count:
            comment(driver, random.choice(comment_list))
            comment_count += 1
        time.sleep(watch_time)


def watch_reels(driver, count, watch_time, likes=None, comments=None):
    global like_count, comment_count
    try:
        reel_link = WebDriverWait(driver, 100).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[aria-label="Reel tile preview"]'))
        )
        reel_link.click()
    except Exception as e:
        logging.error(f"Failed to find reel: {e}")
        return

    logging.info("Watching Reels...")
    for i in range(count):
        if likes and likes > like_count:
            like(driver)
            like_count += 1
        if comments and comments > comment_count:
            comment(driver, random.choice(comment_list))
            comment_count += 1
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '[aria-label="Next card"]'))
            ).click()
        except Exception as e:
            logging.error(f"Failed to find next reel: {e}")
            logging.info(f"Watched {i + 1}/{count} Reels")
            break
        time.sleep(watch_time)
    logging.info(f"{i + 1}/{count} Reels Watched with {driver.session_name}")


def watch_reels_from_username(session_file: str):
    proxy = None
    if config.use_proxy:
        if config.rotating_proxies:
            proxy = extension
        else:
            proxy = proxies[0]
            proxies.pop(0)
    with setup_driver(headless=config.headless, session_name=session_file, proxy=proxy) as driver:
        driver.get("https://www.facebook.com/")
        load_cookies(driver, f'sessions/{session_file}')

        verify_login(driver)

        if post_status(session_file):
            post(driver)

        if not profile_status(session_file):
            bio = getBio()
            setProfile(driver, bio)

        getFriends(driver)
        accept_friend_requests(driver)

        navigate_to_reels(
            driver, f'https://www.facebook.com/{config.username}/reels/')
        watch_reels(driver, config.range, config.watch_time,
                    config.likes, config.comments)


def watch_reels_from_csv():
    with open(config.csv_file, "r") as file:
        reels = csv.reader(file)
        for i in range(0, len(reels), config.threads):
            batch = reels[i:i + config.threads]
            sessions = session_files[i:i + config.threads]
            args = [
                (
                    reel[0],
                    config.watch_time,
                    sessions[index],
                    config.likes,
                    config.comments,
                )
                for index, reel in enumerate(batch)
            ]
            process_batch(watch_reels_from_link, args)


def start_processes(target_func, args_list):
    processes = [multiprocessing.Process(
        target=target_func, args=args) for args in args_list]

    for p in processes:
        p.start()

    for p in processes:
        p.join()


def process_batch(func: callable, sessions_batch: list, size=5):
    with Pool(size) as pool:
        pool.map(func, sessions_batch)


if __name__ == "__main__":

    res = input("Run Main Script (Press 1) / Run Login Script (Press 2): ")

    if res == '2':
        import subprocess
        subprocess.run(['py', 'login.py'])
        exit()

    if config.username:
        for i in range(0, len(session_files), config.threads):
            batch = session_files[i:i + config.threads]
            process_batch(watch_reels_from_username,
                          batch, size=config.threads)

    elif config.use_csv:
        watch_reels_from_csv()

    elif config.livestream_link:
        logging.info(f"Joining Livestream: {config.livestream_link}")
        logging.info(f"Using {config.accounts} Accounts")
        args_list = [
            (
                f'sessions/{session}',
                config.livestream_link,
                config.likes,
                config.comments,
                config.watch_time
            ) for session in session_files
        ]
        start_processes(run_facebook_instance, args_list)
