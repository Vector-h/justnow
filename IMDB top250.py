from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

chrome_options = Options()
chrome_options.add_argument("--headless")  # Run browser in background
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-gpu")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

url = "https://www.imdb.com/chart/top/"
driver.get(url)


time.sleep(5)


movies = driver.find_elements(By.XPATH, '//li[contains(@class,"ipc-metadata-list-summary-item")]')

movie_data = []

rank = 1
for movie in movies:
    try:
        title = movie.find_element(By.XPATH, './/h3').text
        rating = movie.find_element(By.XPATH, './/span[contains(@class,"ipc-rating-star")]').text

        movie_data.append({
            "Rank": rank,
            "Movie Title": title,
            "IMDb Rating": rating
        })

        rank += 1
    except Exception as e:
        print("Error extracting movie:", e)

df = pd.DataFrame(movie_data)
df.to_csv("imdb_top_250_movies.csv", index=False)


driver.quit()

print("IMDb Top 250 Movies scraped successfully!")
