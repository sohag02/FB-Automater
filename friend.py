import time
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import csv

logger = logging.getLogger(__name__)

def getFriends(driver: Chrome):
    logger.info(f"Sending friend requests with {driver.session_name}")
    with open('users.csv', 'r') as f:
        reader = csv.reader(f)
        count = 0
        for row in reader:
            count += 1
            send_friend_request(driver, row[0])
    if count == 0:
        logger.info(f"No users found in users.csv to send friend requests")
    else:
        logger.info(f"Sent {count} friend requests with {driver.session_name}")

def send_friend_request(driver: Chrome, username: str):
    try:
        driver.get(f'https://www.facebook.com/{username}')
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[aria-label="Add friend"]'))
        ).click()
        logger.info(f"Sent friend request to {username} with {driver.session_name}")
    except Exception as e:
        logger.error(f"Failed to send friend request to {username}")

def accept_friend_requests(driver: Chrome):
    logger.info(f"Looking for friend requests with {driver.session_name}")
    driver.get("https://www.facebook.com/friends/requests")
    time.sleep(2)

    count = 0
    while True:
        elem = driver.find_elements(By.CSS_SELECTOR, '[aria-label="Confirm"]')

        if not elem:
            logger.info(f"No friend requests found for {driver.session_name}")
            break

        for element in elem:
            if element.is_displayed():
                try:
                    element.click()
                    count += 1
                    time.sleep(2)
                except:
                    pass
                finally:
                    break
    
    logger.info(f"Accepted {count} friend requests with {driver.session_name}")