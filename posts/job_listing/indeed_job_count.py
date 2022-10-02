# need to wrap to function
# fill key works, must include, loop by colation: state or city, output name
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
import pandas as pd
from selenium.webdriver.chrome.options import Options
from datetime import datetime


options = webdriver.ChromeOptions()
# options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
driver = webdriver.Chrome('./chromedriver', chrome_options=options)


state_names=["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]
dates = []
job_counts = []

for state in state_names:
    driver.get("https://www.indeed.com/advanced_search")

    driver.implicitly_wait(3)

    # search analyst
    search_job = driver.find_element('xpath','//input[@id="as_and"]')
    search_job.send_keys(['analytics'])

    # search location
    searchLocation = driver.find_element('xpath','//input[@id="where"]')
    searchLocation.clear()
    # searchLocation.send_keys("united states")
    searchLocation.send_keys(state)


    # limited to all the time
    result_age = driver.find_element(
        'xpath',
        '//select[@id="fromage"]//option[@value="any"]')
    result_age.click()

    # location: only in
    result_age = driver.find_element(
        'xpath',
        '//select[@id="radius"]//option[@value="0"]')
    result_age.click()

    driver.implicitly_wait(3)

    # push search button
    search_button = driver.find_element('xpath','//*[@id="fj"]')
    search_button.click()
    driver.implicitly_wait(3)

    # Get exact search result amount
    search_count = driver.find_element(
        'xpath',
        "//div[contains(@class,'jobCount')]"
        ).text
    print(state, search_count)
    def sub_str(s, start, end):
        return s[s.find(start)+len(start):s.rfind(end)]
    num = sub_str(search_count, "of ", " jobs")
    job_counts.append(num)

    date = datetime.now().strftime("%m/%d/%Y")
    dates.append(date)

df = pd.DataFrame()
df['date'] = dates
df['state'] = state_names
df['count'] = job_counts

filename = datetime.now().strftime("ost_count_state.csv")
df.reset_index().to_csv(filename)

driver.quit()