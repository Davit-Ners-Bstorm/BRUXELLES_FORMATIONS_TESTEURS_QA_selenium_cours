import time
import uuid

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
CHAMP_CODE = (By.XPATH, "//label[normalize-space()='Code']/following-sibling::input")
CHAMP_REDUCTION = (By.XPATH, "//label[normalize-space()='Reduction (%)']/following-sibling::input")
CHAMP_USAGES = (By.XPATH, "//label[normalize-space()='Usages max']/following-sibling::input")
BOUTON_CREER = (By.XPATH, "//form//button[normalize-space()='Creer']")

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

def saisir(driver, locator, texte):
    champ = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))
    champ.clear()
    champ.send_keys(Keys.CONTROL, "a")
    champ.send_keys(Keys.DELETE)
    champ.send_keys(texte)

def test_activate_deactivate(driver):
    wait = WebDriverWait(driver, 5)
    ouvrir_codes_promo(driver)

    code = "TEST" + uuid.uuid4().hex[:6].upper()

    saisir(driver, CHAMP_CODE, code)
    saisir(driver, CHAMP_REDUCTION, "15")
    saisir(driver, CHAMP_USAGES, "20")

    driver.find_element(*BOUTON_CREER).click()
    new_line = wait.until(EC.presence_of_element_located((By.XPATH, f"//tr[td[normalize-space()='{code}']]")))
    cellules = [cell.text for cell in new_line.find_elements(By.TAG_NAME, 'td')[:5]]

    assert cellules == [code, '-15%', '0/20', '—', 'actif']

    button = new_line.find_element(By.XPATH, ".//button[normalize-space()='Desactiver']")
    button.click()

    badge = (By.XPATH, f"//tr[td[normalize-space()='{code}']]//span")
    wait.until(EC.text_to_be_present_in_element(badge, 'inactif'))

    assert not new_line.find_elements(By.XPATH, ".//button[normalize-space()='Desactiver']")
    # assert new_line.find_elements(By.XPATH, ".//button[normalize-space()='Desactiver']") == []
    # assert len(new_line.find_elements(By.XPATH, ".//button[normalize-space()='Desactiver']")) == 0
