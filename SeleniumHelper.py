from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time, random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import re

class SeleniumHelper:
    def __init__(self, headless=False, maximize_window=True):
        # Set up the webdriver with automatic ChromeDriver download
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')

        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        if maximize_window:
            self.driver.maximize_window()

    def get_page_source(self):
        return self.driver.page_source

    def get_driver(self):
        return self.driver
    def open_url(self, url):
        # Open the specified URL
        self.driver.get(url)

    def find_element(self, by, value, timeout=10):
        # Find a single element on the page
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            print(f"Element {value} not found within {timeout} seconds.")
            return None

    def find_elements(self, by, value, timeout=10):
        # Find multiple elements on the page
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
            return elements
        except TimeoutException:
            print(f"Elements {value} not found within {timeout} seconds.")
            return []

    def click_element(self, by, value, timeout=10):
        # Click on a specified element
        element = self.find_element(by, value, timeout)
        if element:
            element.click()

    def input_text(self, by, value, text, timeout=10):
        # Input text into a specified text field
        element = self.find_element(by, value, timeout)
        if element:
            element.clear()
            element.send_keys(text)

    def close_browser(self):
        # Close the browser
        self.driver.quit()

    def scroll_to_element(self, by, value):
        # Scroll to the specified element
        self.driver.execute_script("window.scrollBy(0, 500);")

        # Wait for the element to become visible (adjust timeout as needed)
        element_to_wait_for = self.find_element(by, value)
        WebDriverWait(self.driver, 10).until(EC.visibility_of(element_to_wait_for))


    def select_dropdown_value(self, by, value, option_text):
            # Select a value from the dropdown
            dropdown = self.find_element(by, f'//select[@id="{value}"]')
            if dropdown:
                dropdown.click()
                option_locator = (by, f'//select[@id="{value}"]/option[text()="{option_text}"]')
                option = self.find_element(*option_locator)
                if option:
                    option.click()

    def wait_for_page_load(self,xpath_val, timeout=10):
        # Wait for the page to load
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.XPATH, xpath_val))
            )
        except TimeoutException:
            print("Page did not load within the specified time.")

    def wait_until_clickable_and_click(self,by,val):
        time.sleep(random.randint(2, 4))
        element = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((by, val)))

        element.click()
    def wait_for_page_to_stop_loading(self, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            print("Page did not finish loading within the specified time.")

    def press_escape(self):
        webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
    def clean_text(self,raw_text):
        # Remove HTML tags
        clean_text = re.sub('<.*?>', '', raw_text)

        # Remove extra whitespaces
        clean_text = ' '.join(clean_text.split())

        # Remove leading and trailing whitespaces
        clean_text = clean_text.strip()

        return clean_text

    def scroll_to_end(self,delay=2):
        """
        Scroll to the end of a webpage using Selenium.

        Parameters:
            - driver: Selenium WebDriver instance.
            - delay: Time delay (in seconds) between scrolling actions. Default is 2 seconds.
        """
        prev_height = 0
        while True:
            # Execute JavaScript to scroll to the bottom of the page
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for a short period to allow the content to load
            time.sleep(delay)

            # Get the current scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            # Break the loop if the scroll height doesn't increase
            if new_height == prev_height:
                break

            prev_height = new_height