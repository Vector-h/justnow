from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# -------------------- CHROME OPTIONS --------------------
options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# -------------------- DRIVER SETUP --------------------
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

url = "https://www.imdb.com/chart/top/"
driver.get(url)

# -------------------- WAIT FOR MOVIES TO LOAD --------------------
wait = WebDriverWait(driver, 15)
wait.until(
    EC.presence_of_element_located(
        (By.CSS_SELECTOR, "ul.ipc-metadata-list li")
    )
)

rows = driver.find_elements(By.CSS_SELECTOR, "ul.ipc-metadata-list li")

movie_list = []

# -------------------- DATA EXTRACTION --------------------
for index, row in enumerate(rows, start=1):
    try:
        title = row.find_element(By.CSS_SELECTOR, "h3").text

        year_elements = row.find_elements(By.CSS_SELECTOR, "span.ipc-inline-list__item")
        year = year_elements[0].text if year_elements else "N/A"

        rating = row.find_element(
            By.CSS_SELECTOR, "span.ipc-rating-star"
        ).text.split()[0]

        movie_list.append({
            "Rank": index,
            "Title": title,
            "Year": year,
            "IMDb Rating": rating
        })

        print(f"{index}. {title} ({year}) - Rating: {rating}")

    except:
        continue


# -------------------- SAVE TO CSV --------------------
df = pd.DataFrame(movie_list)
df.to_csv("imdb_top_250_movies.csv", index=False, encoding="utf-8")

driver.quit()

print("\nIMDb movie list extracted successfully!")
print(f"Total movies scraped: {len(movie_list)}")

