from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import logging

# Setting up logging
logging.basicConfig(filename='scrape_errors.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_driver():
    options = webdriver.ChromeOptions()
    options.binary_location = "/home/kali/Desktop/chrome-linux64/chrome"#path to your chrome binary
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def scrape_postman(search_term):
    driver = initialize_driver()
    try:
        url = f'https://www.postman.com/search?q={search_term}&scope=all&type=all'
        driver.get(url)
        driver.maximize_window()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        actions = ActionChains(driver)
        body_element = driver.find_element(By.TAG_NAME, 'body')
        actions.move_to_element(body_element).click().perform()

        # Scroll using PAGE_DOWN
        for _ in range(50):
            actions.send_keys(Keys.PAGE_DOWN).perform()
            WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))

        links = driver.find_elements(By.TAG_NAME, 'a')
        hrefs_set = set()
        for link in links:
            href = link.get_attribute('href')
            if href and ("workspace" in href or "collection" in href) and href not in ['https://www.postman.com/collection/', 'https://www.postman.com/product/workspaces/']:
                hrefs_set.add(href)

        if hrefs_set:
            tmp_data = {'URLS_SCRAPED': list(hrefs_set), 'SEARCH_TERM_USED': search_term}
            return json.dumps(tmp_data)

    except Exception as e:
        logging.error("Error occurred while scraping Postman: %s", str(e))

    finally:
        driver.quit()

def scrape_workspace_collections(url):
    driver = initialize_driver()
    try:
        driver.get(url)
        driver.maximize_window()
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.collection-sidebar-list__list')))
        process_items(driver, '.collection-sidebar-list__list')

    except Exception as e:
        logging.error("Error occurred while processing workspace collections: %s", str(e))

    finally:
        driver.quit()

def process_items(driver, container_selector):
    items = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, f"{container_selector} > div > div")))
    for item in items:
        driver.execute_script("arguments[0].scrollIntoView(true);", item)
        if 'folder' in item.get_attribute("class"):
            # Click to expand or collapse the folder
            item.click()
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".collection-sidebar-list__list-item__expanded")))  # Adjust the selector as necessary
            process_items(driver, f"{container_selector} > div > div")  # Recursive call to process newly visible items

        elif 'request' in item.get_attribute("class"):
            print(f"Processing request: {item.text}")
            item.click()  # This might expand details or trigger other UI actions

