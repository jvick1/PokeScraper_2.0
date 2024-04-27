# PokeScraper_2.0
This Python script automates collecting Pokémon card data from the website pokellector.com. It retrieves information such as card names, sets, and prices based on user-inputted Pokémon names and saves the data into a CSV file for further analysis.

This script essentially automates gathering Pokémon card data from the specified website for a given Pokémon name and saves it in a CSV file.

## Improvement from V1
In this update, I improved the code structure by breaking it up into functions for a modular design and to improve reusability. 

Each major step in the process can be encapsulated into a function, such as `fetch_page_urls`, `fetch_card_data`, and `save_to_csv`.

### Fetch page URLs

Our fetch url function calls our Chrome drive and navigates to the Pokemon you search for. We then sleep so the page can load and parse the page fetching all the URLs with bs4. 

```py
def fetch_page_urls(driver):
    driver.get("https://www.pokellector.com/search?criteria=" + name + "&x=0&y=0")
    time.sleep(1)
    html = driver.page_source
    soup = bs(html, "html.parser")
    page_urls = [a['href'] for a in soup.select("div.pagination a[href]")]
    return page_urls
```

### Fetch Card Data

For all the URLs we got we then loop over them to pull card-specific data. 

```py
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
```

### Save to CSV

This saves our dataframe to a CSV with the Pokemon's name. 

```py
def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(WD_PATH + filename + ".csv", index=False)
    print(f"Data saved to {WD_PATH}{filename}.csv")
```

### Main

Our `main` is where everything comes together. We start by checking if the main program is running the script. When you run the script from the command line or as a standalone program,. this condition, `__name__ == "__main__"`, will be `True` and execute the code beneath it. Next, we ask the user for the Pokemon name they want to search. We then create a new instance of the ChromeDriver and we use a `try` block to fetch the card data (English & Japanese). Then we use `finally` which is used with `try` blocks to ensure the WebDriver instance closes properly. 

```py
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
```
