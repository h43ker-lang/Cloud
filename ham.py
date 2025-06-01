from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
import time

# Configuration
URL = "https://xhamster.com"
NUM_TABS = 8

# Optional: headless mode (set to False to see browser)
headless = False

# Firefox options
options = Options()
options.headless = headless

# Initialize the Firefox driver
service = FirefoxService()
driver = webdriver.Firefox(service=service, options=options)

# Open the first tab
driver.get(URL)
time.sleep(2)

# Open the rest in new tabs
for _ in range(NUM_TABS - 1):
    driver.execute_script(f'''window.open("{URL}", "_blank");''')
    time.sleep(1)

# Switch to each tab to make sure they load (optional)
for i in range(NUM_TABS):
    driver.switch_to.window(driver.window_handles[i])
    time.sleep(0.5)

print(f"{NUM_TABS} tabs of {URL} opened successfully.")
