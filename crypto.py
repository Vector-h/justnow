from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd, time, os
from datetime import datetime

def driver():
    opt = webdriver.ChromeOptions()
    opt.add_argument("--headless=new")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opt)

def run_scraper():
    d = driver()
    d.get("https://coinmarketcap.com/")
    WebDriverWait(d, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody")))
    
    rows = []
    for r in d.find_elements(By.CSS_SELECTOR, "table tbody tr")[:10]:
        c = r.find_elements(By.TAG_NAME, "td")
        if len(c) > 7:
            rows.append({
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Coin Name": c[2].text.split("\n")[0],
                "Price": c[3].text,
                "24h Change": c[4].text,
                "Market Cap": c[7].text
            })
    d.quit()
    return rows

def save(data):
    file = "crypto_prices_short.csv"
    df = pd.DataFrame(data)
    df.to_csv(file, mode="a", header=not os.path.exists(file), index=False)
    print(df.to_string(index=False), f"\nSaved to: {file}")

if __name__ == "__main__":
    rows = run_scraper()
    if rows: save(rows)
    else: print("No data scraped.")
