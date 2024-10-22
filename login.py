from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import pickle
import time
import csv
import logging
import os
import pandas as pd
from utils import setup_driver, get_proxies
from config import Config
from proxy import check_proxies
from proxy_extension import create_proxy_auth_extension

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


def generate_sessions(email, password):
    proxy = None
    if config.use_proxy:
        if config.rotating_proxies:
            proxy = extension
        else:
            proxy = proxies[0]
            proxies.pop(0)
    try:
        with setup_driver(headless=False, session_name=email, proxy=proxy) as driver:
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
            else:
                success = True

            if success:
                if 'two_step_verification' in driver.current_url:
                    input("Solve the captcha and press any key to continue: ")

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
        # driver.quit()
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
                # Remove the account from the DataFrame
                accounts_df.drop(index, inplace=True)
                # Write the updated DataFrame back to CSV
                accounts_df.to_csv('accounts.csv', index=False)
            else:
                continue
        except Exception as e:
            print("Login Failed for ", row['email'], ' : ', e)
            continue

    print(f'Total {count} Sessions Generated')
