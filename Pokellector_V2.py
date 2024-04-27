from bs4 import BeautifulSoup as bs
from selenium import webdriver
import time
import pandas as pd

WD_PATH = "D:/Python Work Area/01_Py_Automation/data/"
ENG_URL = "https://www.pokellector.com/"
JP_URL = "https://jp.pokellector.com/"

def fetch_page_urls(driver):
    driver.get("https://www.pokellector.com/search?criteria=" + name + "&x=0&y=0")
    time.sleep(1)
    html = driver.page_source
    soup = bs(html, "html.parser")
    page_urls = [a['href'] for a in soup.select("div.pagination a[href]")]
    return page_urls

def fetch_card_data(driver, base_url, page_urls, site):
    card_data = []
    for page_url in page_urls:
        driver.get(base_url + page_url)
        time.sleep(1)
        html = driver.page_source
        soup = bs(html, "html.parser")
        cards = soup.find_all("div", attrs={"class": "cardresult"})
        for card in cards:
            card_name = card.find("div", attrs={"class": "name"}).text.strip()
            card_set = card.find("div", attrs={"class": "set"}).text.strip()
            card_price = card.find("div", attrs={"class": "prices"}).text.strip() if card.find("div", attrs={"class": "prices"}) else "NULL"
            card_data.append({"Name": card_name, "Set": card_set, "Price": card_price, "Site": site})
    return card_data

def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(WD_PATH + filename + ".csv", index=False)
    print(f"Data saved to {WD_PATH}{filename}.csv")

if __name__ == "__main__":
    name = input('Type Pokémon name: ').strip()
    driver = webdriver.Chrome()
    try:
        page_urls = fetch_page_urls(driver)
        eng_cards = fetch_card_data(driver, ENG_URL, page_urls, "English")
        jp_cards = fetch_card_data(driver, JP_URL, page_urls, "Japanese")
        all_cards = eng_cards + jp_cards
        save_to_csv(all_cards, name)
    finally:
        driver.quit()
