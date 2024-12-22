from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# Set up the path to your ChromeDriver
chrome_driver_path = r'C:\Users\sapta\Downloads\chromedriver\chromedriver.exe'  # Change this to your ChromeDriver path

# Create a Service object
service = Service(chrome_driver_path)

# Set up the Selenium WebDriver with the Service object
driver = webdriver.Chrome(service=service)

def wait_for_element(driver, by, value, timeout=60):
    """Wait for an element to be present on the page."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        print(f"Timeout: Element with {by}='{value}' not found within {timeout} seconds.")
        return None

try:
    # Step 1: Go to the website
    driver.get('https://4rabetsite.com/')

    # Step 2: Click on the Aviator link
    aviator_link = wait_for_element(driver, By.CSS_SELECTOR, 'a[data-auto-test-el="aviatorSections"]')
    if aviator_link:
        aviator_link.click()

    # Wait for the sign-in popup to appear
    time.sleep(2)  # Adjust sleep time if necessary

    # Step 3: Enter the email
    email_input = wait_for_element(driver, By.ID, 'login-email-input')
    if email_input:
        email_input.send_keys('saptarshiabhi21@gmail.com')  # Replace with your email

    # Step 4: Enter the password
    password_input = wait_for_element(driver, By.ID, 'login-pwd-input')
    if password_input:
        password_input.send_keys('Abcd@1234')  # Replace with your password

    # Step 5: Click the Sign in button
    sign_in_button = wait_for_element(driver, By.ID, 'login-sign-in-btn', timeout=10)
    if sign_in_button:
        sign_in_button.click()

    # Wait for login to process
    time.sleep(30)  # Adjust sleep time if necessary

    # Step 6: Click on the Aviator link again (if needed)
    aviator_link = wait_for_element(driver, By.CSS_SELECTOR, 'a[data-auto-test-el="aviatorSections"]')
    if aviator_link:
        aviator_link.click()

    # Initialize variables for tracking multipliers
    previous_first_multiplier = None
    previous_length = 0

    while True:
        # Switch to the iframe containing the bubble-multiplier elements
        try:
            iframe = wait_for_element(driver, By.TAG_NAME, 'iframe', timeout=10)
            driver.switch_to.frame(iframe)
        except Exception as e:
            print(f"Error switching to iframe: {e}")
            time.sleep(5)  # Wait before retrying
            continue

        # Wait for the bubble-multiplier elements to load
        multipliers = wait_for_element(driver, By.CLASS_NAME, 'bubble-multiplier', timeout=60)

        if multipliers is None:
            print("No multipliers found. Retrying...")
            driver.switch_to.default_content()  # Switch back to the main content
            time.sleep(5)  # Wait before retrying
            continue

        # Scrape data from the page
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find all bubble-multiplier elements
        multipliers = soup.find_all(class_='bubble-multiplier')

        # Check if multipliers were found
        if not multipliers:
            print("No multipliers found. Retrying...")
            driver.switch_to.default_content()  # Switch back to the main content
            time.sleep(5)  # Wait before retrying
            continue

        # Extract multiplier values
        current_values = [multiplier.get_text(strip=True) for multiplier in multipliers]
        print("Current multipliers:", current_values)  # Debugging line

        # Check the first multiplier
        first_multiplier = current_values[0]
        current_length = len(current_values)

        # On the first iteration, save all multipliers
        if previous_first_multiplier is None:
                        # Save all multipliers to CSV
            df = pd.DataFrame(current_values, columns=['Multiplier'])
            df.to_csv('multipliers.csv', mode='a', header=not os.path.exists('multipliers.csv'), index=False)
            print(f"Saved initial multipliers to CSV: {current_values}")

        else:
            # Compare the first multiplier and lengths
            if first_multiplier == previous_first_multiplier:
                if current_length > previous_length:
                    # If the first multiplier is the same but the new list is longer, save the first multiplier
                    df = pd.DataFrame([first_multiplier], columns=['Multiplier'])
                    df.to_csv('multipliers.csv', mode='a', header=False, index=False)
                    print(f"Saved first multiplier to CSV: {first_multiplier}")
            else:
                # If the first multiplier is different, save the new first multiplier
                df = pd.DataFrame([first_multiplier], columns=['Multiplier'])
                df.to_csv('multipliers.csv', mode='a', header=False, index=False)
                print(f"Saved new first multiplier to CSV: {first_multiplier}")

        # Update the previous first multiplier and length for the next iteration
        previous_first_multiplier = first_multiplier
        previous_length = current_length

        # Switch back to the main content for the next iteration
        driver.switch_to.default_content()

        # Wait for a specified time before checking again
        time.sleep(5)  # Adjust the sleep time as needed

finally:
    driver.quit()  # Close the browser after scraping