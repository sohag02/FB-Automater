from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from undetected_chromedriver import Chrome
import pickle
import time
import csv
import logging
import os
import pandas as pd

logging.getLogger('selenium').setLevel(logging.ERROR)

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument('--log-level=3')  # Suppress logs
    return Chrome(options=chrome_options)


def generate_sessions(email, password):
    try:
        driver = setup_driver()
        driver.get("https://www.facebook.com/")

        # Enter email and password
        driver.find_element("id", "email").send_keys(email)
        driver.find_element("id", "pass").send_keys(password)
        driver.find_element(By.NAME, "login").click()

        # Wait for login to complete (adjust timing as needed)
        time.sleep(10)
        if 'disabled' in driver.current_url:
            print(f"Login Failed for {email}. Account is Disabled")
            success = False
        
        if success:
            try:
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, '[aria-label="Your profile"]'))
                )
                success = True
            except Exception:
                print(f"Login Failed for {email}")
                success = False

        if success:
            # Save cookies to a file
            cookies = driver.get_cookies()
            with open(f'sessions/{email}.pkl', "wb") as file:
                pickle.dump(cookies, file)

            print(f"Session Generated for {email}")

    except Exception as e:
        print(f"Login Failed for {email}")
    finally:
        driver.quit()
        return success

if __name__ == "__main__":
    # Verify sessions folder
    if not os.path.exists("sessions"):
        os.makedirs("sessions")

    # created.csv
    if not os.path.exists('created.csv'):
        with open('created.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['email', 'password'])

    count = 0
    accounts_df = pd.read_csv('accounts.csv')  # Read accounts into a DataFrame

    for index, row in accounts_df.iterrows():
        try:
            if success := generate_sessions(row['email'], row['password']):
                with open('created.csv', 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([row['email'], row['password']])
                count += 1
                accounts_df.drop(index, inplace=True)  # Remove the account from the DataFrame
                accounts_df.to_csv('accounts.csv', index=False)  # Write the updated DataFrame back to CSV
            else:
                continue
        except Exception as e:
            print("Login Failed for ", row['email'], ' : ', e)
            continue

    print(f'Total {count} Sessions Generated')
