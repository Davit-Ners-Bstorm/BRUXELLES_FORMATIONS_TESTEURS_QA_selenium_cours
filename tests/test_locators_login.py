from tests.config import BASE_URL
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest

LOCATORS_EX2 = [
    (By.CSS_SELECTOR, "input[type=email]"), # INPUT EMAIL CSS
    (By.CSS_SELECTOR, "input[type=password]"), # INPUT MDP CSS
    (By.XPATH, "//label[normalize-space()='Mot de passe']/following-sibling::input"), # INPUT MDP XPATH
    (By.CSS_SELECTOR, "form .btn-primary"), # BUTTON SE CONNECTER CSS
    (By.XPATH, "//button[normalize-space()='Se connecter']"), # BUTTON SE CONNECTER XPATH
]

@pytest.mark.parametrize("locator", LOCATORS_EX2, ids=lambda loc: loc[1]) # ids version comprehension de lsit : [loc[1] for loc in LOCATORS_EX2]
def test_locators(driver, locator):
    driver.get(f"{BASE_URL}/login")

    element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

    assert element
