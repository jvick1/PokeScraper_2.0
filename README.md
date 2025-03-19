# PokeScraper_2.0
This Python script automates collecting Pokémon card data from the website pokellector.com. It retrieves information such as card names, sets, and prices based on user-inputted Pokémon names and saves the data into a CSV file for further analysis.

This script essentially automates gathering Pokémon card data from the specified website for a given Pokémon name and saves it in a CSV file.

## Improvement from V1
In this update, I improved the code structure by breaking it up into functions for a modular design and to improve reusability. 

Each major step in the process can be encapsulated into a function, such as `fetch_page_urls`, `fetch_card_data`, and `save_to_csv`.

### Fetch page URLs

Our fetch url function calls our Chrome drive and navigates to the Pokemon you search for. We then sleep so the page can load and parse the page fetching all the URLs with bs4. 

```py
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
```

### Fetch Card Data

For all the URLs we got we then loop over them to pull card-specific data. 

```py

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
```

### Save to CSV

This saves our dataframe to a CSV with the Pokemon's name. 

```py
def save_to_csv(data, filename):
    """
    Saves a list of card data to a CSV file.
    """
    df = pd.DataFrame(data)
    df.to_csv(WD_PATH + filename + ".csv", index=False)
    print(f"Data saved to {WD_PATH}{filename}.csv")
```

### Main

Our `main` is where everything comes together. We start by checking if the main program is running the script. When you run the script from the command line or as a standalone program,. this condition, `__name__ == "__main__"`, will be `True` and execute the code beneath it. Next, we ask the user for the Pokemon name they want to search. We then create a new instance of the ChromeDriver and we use a `try` block to fetch the card data (English & Japanese). Then we use `finally` which is used with `try` blocks to ensure the WebDriver instance closes properly. 

```py
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
```
