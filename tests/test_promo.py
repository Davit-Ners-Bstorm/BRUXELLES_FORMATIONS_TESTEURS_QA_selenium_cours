import pytest
from pytest import mark
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tests.config import BASE_URL, CLIENT_EMAIL, CLIENT_PASSWORD, ORGA_EMAIL, ORGA_PASSWORD
from selenium.webdriver.common.by import By



EMAIL = (By.CSS_SELECTOR, "input[type=email]")
PASSWORD = (By.CSS_SELECTOR, "input[type=password]")
SUBMIT = (By.CSS_SELECTOR, "form button.btn-primary")
DECONNEXION = (By.XPATH, "//button[normalize-space()='Deconnexion']")
CELLULES_CODE = (By.CSS_SELECTOR, "table.table tbody td.mono")

def ouvrir_codes_promo(driver: webdriver.Chrome):
    driver.get(f"{BASE_URL}/login")
    wait = WebDriverWait(driver, 5)

    email_input = wait.until(EC.visibility_of_element_located(EMAIL))
    email_input.clear()
    email_input.send_keys(ORGA_EMAIL)

    password_input = driver.find_element(*PASSWORD)
    password_input.clear()
    password_input.send_keys(ORGA_PASSWORD)

    btn_login = driver.find_element(*SUBMIT)
    btn_login.click()

    wait.until(EC.visibility_of_element_located(DECONNEXION))

    driver.get(f"{BASE_URL}/admin/promos")
    wait.until(EC.visibility_of_element_located(CELLULES_CODE))


def test_promo_codes_listed(driver):
    ouvrir_codes_promo(driver)

    cells = [cell.text for cell in driver.find_elements(*CELLULES_CODE)]
    assert 'WELCOME10' in cells
    assert 'VIP25' in cells
    assert 'EXPIRED' in cells

@mark.parametrize("code, status, nb_btn", [
    ("WELCOME10", "actif", 1),
    ("VIP25", "inactif", 0),
    ("EXPIRED", "inactif", 0)
], ids=["WELCOME is active", "VIP is inactive", "EXPIRED is inactive"])
def test_promo_status(driver, code, status, nb_btn):
    ouvrir_codes_promo(driver)

    badge = driver.find_element(By.XPATH, f"//tr[td[normalize-space()='{code}']]//span[contains(@class,'badge')]")
    buttons = driver.find_elements(By.XPATH, f"//tr[td[normalize-space()='{code}']]//button[normalize-space()='Desactiver']")

    assert badge.text == status
    assert len(buttons) == nb_btn