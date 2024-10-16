from db import get_user_profile, update_user_profile
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import Chrome
from post import getImage
import os
import logging
import random

logger = logging.getLogger(__name__)


def isProfileSet(session):
    user_profile = get_user_profile(session)
    if user_profile:
        return user_profile.profile_setup
    return False


def get_profile_pic():
    if not os.path.exists('./profile_photos'):
        logger.error("No Profile Photos Found in folder")

    photos = os.listdir('./profile_photos')
    if photos:
        photo = random.choice(photos)
        path = f'{os.getcwd()}\\profile_photos\\{photo}'
        return path
    logging.error("No Profile Photos Found")
    return None


def open_profile(driver: Chrome):
    driver.get("https://www.facebook.com/me")


def chanage_profile_pic(driver: Chrome):
    try:
        logging.info(f"Changing Profile Pic for {driver.session_name}")
        image = get_profile_pic()
        if not image:
            return

        open_profile(driver)

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[aria-label="Update profile picture"]'))
        ).click()
        time.sleep(5)
        to_remove = driver.find_element(By.XPATH, "//input[@type='file']")
        # Execute JavaScript to remove the element
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, to_remove)

        file_input = driver.find_element(By.XPATH, "//input[@type='file']")

        driver.execute_script(
            "arguments[0].style.display = 'block';", file_input)
        driver.execute_script("arguments[0].click();", file_input)

        file_input.send_keys(image)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[aria-label="Save"]'))
        ).click()
        logger.info(f"Successfully changed profile picture for {driver.session_name}")
    except Exception as e:
        logger.error(f"Failed to change profile pic: {e}")
        raise
    finally:
        if image:
            try:
                os.remove(image)
            except:
                pass


def set_bio(driver: Chrome, bio: str):
    open_profile(driver)
    try:
        bio_btn = driver.find_element(
            By.CSS_SELECTOR, '[aria-label="Add Bio"]')
    except:
        # driver.find_element(By.CSS_SELECTOR, '[aria-label="Edit Bio"]')
        return

    logger.info(f'Setting Bio for {driver.session_name}')
    bio_btn.click()

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '[aria-label="Enter bio text"]'))
    ).send_keys(bio)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Save"]'))
    ).click()
    time.sleep(2)


def change_cover_photo(driver: Chrome):
    try:
        open_profile(driver)
        image = getImage(size='820/360')

        file_input = driver.find_element(By.XPATH, "//input[@type='file']")

        driver.execute_script(
            "arguments[0].style.display = 'block';", file_input)
        driver.execute_script("arguments[0].click();", file_input)

        file_input.send_keys(f'{os.getcwd()}\\{image}')
        time.sleep(5)
        # Finding and clicking the element in a single script using JavaScript
        # driver.execute_script("document.querySelector('[aria-label=\"Save changes\"]').click();")
        # driver.execute_script("arguments[0].click();", element)
        # driver.find_element(By.CSS_SELECTOR, '[aria-label="Save changes"]').click()
        save_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[aria-label="Save changes"]'))
        )
        save_btn.click()
        logger.info(f"Successfully changed cover photo for {
                     driver.session_name}")
    except:
        # logger.error(f"Failed to change cover photo: {e}")
        raise
    finally:
        os.remove(image)

def setProfile(driver: Chrome, bio: str):
    set_bio(driver, bio)
    # change_cover_photo(driver)
    chanage_profile_pic(driver)
    update_user_profile(driver.session_name, profile_setup=True)