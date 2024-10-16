import random
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils import comment, get_comments, like, load_cookies, setup_driver

like_count = 0
comment_count = 0


def run_facebook_instance(cookies_file, url, likes=None, comments=None, watch_time=None):
    global like_count, comment_count
    with setup_driver(headless=True, session_name=cookies_file.replace("sessions/", "")) as driver:
        if comments:
            comment_list = get_comments()

        # Login
        driver.get("https://www.facebook.com/")
        load_cookies(driver, cookies_file)
        time.sleep(5)

        # Navigate to live stream
        driver.get(url)
        time.sleep(5)  # Allow the page to load and interact with it

        # Start watching the stream
        start_time = time.time()

        # Perform like action if specified
        if likes and likes > like_count:
            like(driver)
            like_count += 1

        # Perform comment action if specified
        if comments and comments > comment_count:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '[aria-label="Leave a comment"]'))
            ).click()
            comment(driver, random.choice(comment_list))
            comment_count += 1

        while True:

            # Check if watch_time is provided and has elapsed
            if watch_time and (time.time() - start_time) >= watch_time:
                break

            # Check if the stream has ended by looking for an element that indicates the end of the stream
            try:
                stream_end_element = driver.find_element(By.CSS_SELECTOR, '[aria-label="Stream has ended"]')
                if stream_end_element:
                    print("Stream has ended.")
                    break
            except:
                pass

            time.sleep(5)  # Check the conditions every 5 seconds