from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

options = Options()
options.add_argument("--headless")  # remove this line if you want to SEE the browser
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

url = "https://www.imdb.com/chart/top/"
driver.get(url)
time.sleep(5)
-
rows = driver.find_elements(By.CSS_SELECTOR, "ul.ipc-metadata-list li")

movie_list = []

for index, row in enumerate(rows, start=1):
    try:
        title = row.find_element(By.CSS_SELECTOR, "h3").text
        year = row.find_element(By.CSS_SELECTOR, "span.ipc-inline-list__item").text
        rating = row.find_element(By.CSS_SELECTOR, "span.ipc-rating-star").text

        movie_list.append({
            "Rank": index,
            "Title": title,
            "Year": year,
            "IMDb Rating": rating
        })

        print(f"{index}. {title} ({year}) - Rating: {rating}")

    except Exception:
        continue

# -------------------------------
# Save to CSV
# -------------------------------
df = pd.DataFrame(movie_list)
df.to_csv("imdb_top_250_movies.csv", index=False)

driver.quit()

print("\nIMDb movie list extracted successfully!")
print(f" Total movies scraped: {len(movie_list)}")
