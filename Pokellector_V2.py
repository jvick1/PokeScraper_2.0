from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
import time
import pandas as pd
from tqdm import tqdm

WD_PATH = "E:/Code/Python/01_Py_Automation/data/"
ENG_URL = "https://www.pokellector.com/"
JP_URL = "https://jp.pokellector.com/"

def fetch_page_urls(driver, base_url, name):
    """
    Fetches pagination URLs for a Pokémon search from a given site.
    """
    search_url = f"{base_url}/search?criteria={name}"

    try:
        driver.get(search_url)
        time.sleep(1)
        html = driver.page_source
        soup = bs(html, "html.parser")
        page_urls = [a['href'].replace(base_url, '') for a in soup.select("div.pagination a[href]")]
        # If no pagination links, use the search page itself
        if not page_urls:
            page_urls = [search_url.replace(base_url, '')]  # Relative URL
        return page_urls
    except WebDriverException as e:
        time.sleep(2)

def fetch_card_data(driver, base_url, page_urls, site, timeout=2):
    """
    Scrapes card data from a list of page URLs for a given site.
    """
    card_data = []
    for page_url in tqdm(page_urls, desc=f"Fetching {site} cards"):
    
        try:
            full_url = base_url + page_url
            driver.get(full_url)
            
            # Wait for page to stabilize (document.readyState == 'complete') or timeout
            try:
                WebDriverWait(driver, timeout).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                print(f"{site} - {full_url}: Page loaded normally")
            except TimeoutException:
                print(f"{site} - {full_url}: Still loading after {timeout}s, stopping refresh")
                driver.execute_script("window.stop();")  # Stop the refresh/loading

            # Use whatever HTML is available
            html = driver.page_source
            soup = bs(html, "html.parser")
            cards = soup.find_all("div", attrs={"class": "cardresult"})
            print(f"{site} - {full_url}: Found {len(cards)} cards")

            for card in cards:
                card_name = card.find("div", attrs={"class": "name"}).text.strip()
                card_set = card.find("div", attrs={"class": "set"}).text.strip()
                card_price = card.find("div", attrs={"class": "prices"}).text.strip() if card.find("div", attrs={"class": "prices"}) else "NULL"
                card_data.append({"Name": card_name, "Set": card_set, "Price": card_price, "Site": site})
            
        except WebDriverException as e:
            time.sleep(2)
    return card_data

def save_to_csv(data, filename):
    """
    Saves a list of card data to a CSV file.
    """
    df = pd.DataFrame(data)
    df.to_csv(WD_PATH + filename + ".csv", index=False)
    print(f"Data saved to {WD_PATH}{filename}.csv")

if __name__ == "__main__":
    names_input = input('Type Pokémon names (comma-seprated): ').strip()
    driver = webdriver.Chrome()
    try:
        for name in names_input.split(','):
            name=name.strip()
            print(f"Processing {name}...")
            eng_page_urls = fetch_page_urls(driver, ENG_URL, name)
            jp_page_urls = fetch_page_urls(driver, JP_URL, name)
            eng_cards = fetch_card_data(driver, ENG_URL, eng_page_urls, "English")
            jp_cards = fetch_card_data(driver, JP_URL, jp_page_urls, "Japanese")
            all_cards = eng_cards + jp_cards
            save_to_csv(all_cards, name)
    finally:
        driver.quit()
