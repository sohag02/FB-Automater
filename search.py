import time
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os
import logging
import csv

from utils import wait_for_page_load

logger = logging.getLogger(__name__)


def scroll_down(driver: Chrome):
    driver.execute_script("window.scrollBy(0, 500);")


def search(driver: Chrome, query: str, search_duration, name, user_id=None, username=None):
    if not user_id and not username:
        raise ValueError('Either user_id or username must be provided')

    driver.get(f'https://www.facebook.com/search/pages/?q={query}')
    wait_for_page_load(driver)

    if user_id:
        acc_url = f'https://www.facebook.com/profile.php?id={user_id}'
    else:
        acc_url = f'https://www.facebook.com/@{username}'

    start_time = time.time()

    logging.info(f'Searching for profile {username or user_id}...')
    while time.time() - start_time < search_duration:
        try:
            # WebDriverWait(driver, 2).until(
            #     EC.element_to_be_clickable(
            #         (By.XPATH, f'//a[starts-with(@href, "{acc_url}") and @aria-label="{name}" and text()="{name}"]'))
            # ).click()
            driver.find_element(
                By.XPATH, f'//a[starts-with(@href, "{acc_url}") and @aria-label="{name}"]'
            ).click()
            break
        except Exception as e:
            print(e)
            time.sleep(2)
            scroll_down(driver)
