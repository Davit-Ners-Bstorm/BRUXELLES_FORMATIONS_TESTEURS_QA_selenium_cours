from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from tests.config import BASE_URL
from selenium.webdriver import Keys

class LoginPage:
    EMAIL = (By.CSS_SELECTOR, "input[type=email]")

    def __init__(self, driver: "webdriver.Chrome"):
        self.driver = driver
        self.wait = WebDriverWait(driver, 6)

    def ouvrir(self):
        self.driver.get(BASE_URL + "/login")
        self.wait.until(EC.visibility_of_element_located(self.EMAIL))
        return self

    def saisir(self, locator: tuple[str, str], text: str):
        champ = self.wait.until(EC.visibility_of_element_located(locator))
        champ.clear()
        champ.send_keys(Keys.CONTROL, "a")
        champ.send_keys(Keys.DELETE)
        champ.send_keys(text)
        return self
    



my_driver = webdriver.chrome()

page = LoginPage(my_driver)
page.ouvrir()
page.saisir(page.EMAIL, 'orga@eventflow.com')
