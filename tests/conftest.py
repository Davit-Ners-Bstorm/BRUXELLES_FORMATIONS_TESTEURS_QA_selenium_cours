import os
from dotenv import load_dotenv
from selenium import webdriver
import pytest

load_dotenv()

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()

    if os.getenv("HEADLESS", "true").lower() == "true":
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1366,900")

    drv = webdriver.Chrome(options=options)

    yield drv

    drv.quit()
