import time
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from datetime import datetime
from db import update_user_profile
import logging
from utils import getImage, getCaption

logger = logging.getLogger(__name__)

def post(driver: Chrome):
    logger.info(f"Posting for {driver.session_name}")
    try:
        driver.get("https://www.facebook.com/")
        caption = getCaption()
        # Open post box
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(text(), \"What's on your mind\")]"))
        ).click()

        # Write caption
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(@aria-label, \"What's on your mind\")]"))
        ).send_keys(caption)

        logger.info("Downloading Post Image...")
        file = getImage()
        logger.info(f'Saved as {file}')
        # Post
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[aria-label="Photo/video"]'))
        ).click()
        file_input = driver.find_element(By.XPATH, "//input[@type='file']")

        driver.execute_script("arguments[0].style.display = 'block';", file_input)
        file_input.send_keys(os.getcwd() + f'/{file}')
        time.sleep(5)

        # Click post Btn
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[aria-label="Post"]'))
        ).click()
        
        update_user_profile(driver.session_name, datetime.now().date())
        time.sleep(10)
        logger.info(f"Successfully posted with {driver.session_name}")
    except Exception as e:
        logger.error(f"Failed to post with {driver.session_name}")
    finally:
        if file:
            os.remove(file)
