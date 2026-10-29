from selenium.webdriver import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tests.config import BASE_URL
from selenium.webdriver.common.by import By
import pytest
import time

EMAIL_INPUT = (By.CSS_SELECTOR, "input[type=email]")
PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type=password]")
LOGIN_BTN = (By.CSS_SELECTOR, "form .btn-primary")
ERROR = (By.CSS_SELECTOR, ".notice-err")


def test_incorrect_login(driver):
    driver.get(f"{BASE_URL}/login")
    wait = WebDriverWait(driver, 10)

    # Trouver et completer email
    email_input = wait.until(EC.visibility_of_element_located(EMAIL_INPUT))
    email_input.clear()
    email_input.send_keys("hzjhkrzty@aefaef")

    # Trouver et completer mdp
    password_input = driver.find_element(*PASSWORD_INPUT)
    password_input.clear()
    password_input.send_keys("aefaef")

    login_btn = driver.find_element(*LOGIN_BTN)
    login_btn.click()

    # Pour voir execution
    # time.sleep(5)

    # BAM erreur corrigée!
    error_msg = wait.until(EC.visibility_of_element_located(ERROR))

    assert error_msg.text == "Incorrect email or password"
    assert driver.current_url == f"{BASE_URL}/login"

def test_vraie_suppression_state_react_bizzare(driver):
    driver.get(f"{BASE_URL}/login")

    email_input = driver.find_element(*EMAIL_INPUT)
    password_input = driver.find_element(*PASSWORD_INPUT)

    email_input.click()
    # Ici, on selectionne element, puis on supprime avec controls clavier, ce qui met à jour le state de react
    email_input.send_keys(Keys.CONTROL, "a")
    email_input.send_keys(Keys.BACKSPACE)

    password_input.click()
    password_input.send_keys(Keys.CONTROL, "a")
    password_input.send_keys(Keys.BACKSPACE)

    assert email_input.get_property("value") == ""
    assert password_input.get_property("value") == ""

    email_input.send_keys("123456")

    assert email_input.get_property("value") == "123456"
    assert password_input.get_property("value") == ""
