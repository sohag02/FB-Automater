import json
import logging
import os
import random
import time

import pandas as pd
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import Config
from main import load_sessions
from proxy import check_proxies
from proxy_extension import create_proxy_auth_extension
from utils import (
    get_proxies,
    load_cookies,
    setup_driver,
    verify_login,
    wait_for_page_load,
)

config = Config()

logging.getLogger('selenium').setLevel(logging.ERROR)

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

def get_media(path='media'):
    medias = os.listdir(path)
    return random.choice(medias)

def send_message(driver:Chrome, user_id):
    with open('messages.json', 'r') as f:
        messages = json.load(f)['messages']

    try:
        int(user_id)
        link = f"https://www.facebook.com/profile.php?id={user_id}"
    except:
        link = f'https://www.facebook.com/{user_id}'

    driver.get(link)
    wait_for_page_load(driver)
    # scroll_down(driver)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '[aria-label="Message"]'))
    ).click()
    time.sleep(2)

    text_box = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//div[@aria-label='Message' and @aria-placeholder='Aa']"))
    )
    
    for i in range(config.media_msg_sequence):
        if i == config.media_msg_sequence-1:
            media = get_media()
            attach_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Attach a file"]'))
                )
            text_box.send_keys(Keys.ENTER)
            file_input = attach_button.find_element(By.XPATH, "ancestor::*//input[@type='file']")
            # file_input
            driver.execute_script("arguments[0].style.display = 'block';", file_input)
            file_input = attach_button.find_element(By.XPATH, "ancestor::*//input[@type='file']")
            file_input.send_keys(f'{os.getcwd()}\\media\\{media}')
            time.sleep(2)
            text_box.send_keys(Keys.ENTER)
            time.sleep(2)
            break
        else:
            text_box.send_keys(messages[i])
            text_box.send_keys(Keys.ENTER)
            time.sleep(2)

    # close chat
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '[aria-label="Close chat"]'))
    ).click()

def main():
    sessions = load_sessions(count=None)
    logging.info(f"{len(sessions)} Sessions Found")
    users = pd.read_csv(config.csv_file, header=None, index_col=None)
    # users = users.sample(config.users)
    user_count = 0
    processed_users = set()
    while user_count < config.users:
        
        logging.info(f"Sending message to {config.users} users")
        proxy = None
        if config.use_proxy:
            if config.rotating_proxies:
                proxy = extension
            else:
                proxy = proxies[0]
                proxies.pop(0)
        try:
            session_file = sessions[0]
        except IndexError:
            logging.error("No More sessions found")
            break
        sessions.pop(0)

        last_index = 0

        with setup_driver(session_file, config.headless, proxy=proxy) as driver:
            driver.get("https://www.facebook.com/")
            load_cookies(driver, f'sessions/{session_file}')
            verify_login(driver)
            for user in users.iloc[last_index:last_index+config.msg_per_session, 0]:
                # user
                logging.info(f"Sending message to {user} from {session_file}")
                send_message(driver, user)
                user_count += 1
                last_index += 1
                # delete user from csv
                # updated_users = users[users[0] != user]     
                # updated_users.to_csv(config.csv_file, header=False, index=False)
                processed_users.add(user)
                # write user to done.csv
                with open('done.csv', 'a') as f:
                    f.write(f'{user}\n')
    
    remaining_users = users[~users[0].isin(processed_users)]
    remaining_users.to_csv(config.csv_file, header=False, index=False)
    logging.info(f"Messages sent to {user_count} users")


if __name__ == "__main__":
    main()
        
