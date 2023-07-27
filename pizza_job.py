import datetime

from sqlalchemy import create_engine
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from subprocess import CREATE_NO_WINDOW
import selenium.webdriver.support.expected_conditions as ec

# TODO: Consider creating a custom Job class


def run():
    df_restaurants = _get_restaurants()

    if len(df_restaurants) > 0:
        _insert_into_db(df_restaurants)
        return True
    else:
        return False


def _get_chromedriver():
    """ Initializes the chrome driver for later usage """
    chrome_service = Service("chromedriver")
    chrome_service.creation_flags = CREATE_NO_WINDOW

    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    return webdriver.Chrome(service=chrome_service, options=options)


def _get_restaurants() -> pd.DataFrame:
    """ Accesses the website and fetches all open restaurants along with their delivery prices """
    driver = _get_chromedriver()
    driver.get("https://www.kotipizza.fi/#AddressSelectionSummaryModal")

    WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.NAME, "address-search")))
    driver.find_element(By.NAME, "address-search").send_keys("Address 123")

    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.ID, "address-autocomplete-option-0")))
    driver.find_element(By.NAME, "address-search").send_keys(Keys.ENTER)

    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'sc-jsTgWu hStBJK')]")))
    restaurants = driver.find_elements(By.XPATH, "//div[contains(@class, 'sc-jsTgWu hStBJK')]")

    name_price_list = []
    for restaurant in restaurants:
        text = restaurant.text.split("\n")
        name_price_list.append({"Restaurant": text[0].split(" ")[1][:-1], "Price": float(text[3][:4].replace(",", "."))})

    driver.close()

    df_restaurants = pd.DataFrame(name_price_list)
    df_restaurants["Time_stamp"] = pd.to_datetime(datetime.datetime.now())

    return df_restaurants


def _insert_into_db(data):
    """ Appends new data to the database """
    engine = create_engine("sqlite:///db_pizza.sqlite", echo=False)
    data.to_sql("delivery_prices", con=engine, if_exists="append", index=False)
