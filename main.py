import datetime
import time

import schedule

from sqlalchemy import create_engine

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as ec


def main():
    df_restaurants = pd.DataFrame(get_restaurants())
    df_restaurants["Time_stamp"] = pd.to_datetime(datetime.datetime.now())

    insert_into_db(df_restaurants)


def get_restaurants() -> list:
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver = webdriver.Chrome(options=options)

    driver.get("https://www.kotipizza.fi/#AddressSelectionSummaryModal")

    WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.NAME, "address-search")))
    driver.find_element(By.NAME, "address-search").send_keys("ADDRESS 123")

    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.ID, "address-autocomplete-option-0")))
    driver.find_element(By.NAME, "address-search").send_keys(Keys.ENTER)

    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'sc-jsTgWu hStBJK')]")))
    restaurants = driver.find_elements(By.XPATH, "//div[contains(@class, 'sc-jsTgWu hStBJK')]")

    name_price_list = []
    for restaurant in restaurants:
        text = restaurant.text.split("\n")
        name_price_list.append({"Restaurant": text[0].split(" ")[1][:-1], "Price": float(text[3][:4].replace(",", "."))})

    driver.close()

    return name_price_list


def insert_into_db(data):
    engine = create_engine("sqlite:///db_pizza.sqlite", echo=False)
    data.to_sql("delivery_prices", con=engine, if_exists="append", index=False)


if __name__ == "__main__":
    main()
    schedule.every(10).minutes.do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)
