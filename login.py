from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import pickle
import time
import csv
import logging
import os

logging.getLogger('selenium').setLevel(logging.ERROR)

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument('--log-level=3')  # Suppress logs
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def generate_sessions(driver: webdriver.Chrome, email, password):
    try:
        driver.get("https://www.facebook.com/")

        # Enter email and password
        driver.find_element("id", "email").send_keys(email)
        driver.find_element("id", "pass").send_keys(password)
        driver.find_element(By.NAME, "login").click()

        # Wait for login to complete (adjust timing as needed)
        time.sleep(10)
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '[aria-label="Your profile"]'))
            )
            success = True
        except:
            print("Login Failed for " + email)
            success = False
            return

        # Save cookies to a file
        cookies = driver.get_cookies()
        with open(f'sessions/{email}.pkl', "wb") as file:
            pickle.dump(cookies, file)

        print("Session Generated for " + email)

    except Exception as e:
        print("Login Failed for " + email)
    finally:
        # Logout
        driver.delete_all_cookies()
        driver.refresh()
        return success

if __name__ == "__main__":
    # Verify sessions folder
    if not os.path.exists("sessions"):
        os.makedirs("sessions")

    driver = setup_driver()
    count = 0
    with open('accounts.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            try:
                success = generate_sessions(driver,row[0], row[1])
                if success:
                    count += 1
            except Exception as e:
                print("Login Failed for ", row[0], ' : ', e)
                continue
    driver.quit()
    print(f'Total {count} Sessions Generated')