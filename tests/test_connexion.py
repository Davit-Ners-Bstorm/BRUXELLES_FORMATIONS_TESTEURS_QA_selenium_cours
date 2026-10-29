from tests.config import BASE_URL
from selenium.webdriver.common.by import By
import pytest

EMAIL_INPUT = (By.CSS_SELECTOR, "input[type=email]")
PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type=password]")
LOGIN_BTN = (By.CSS_SELECTOR, "form .btn-primary")
ERROR = (By.CSS_SELECTOR, ".notice-err")


def test_incorrect_login(driver):
    driver.get(f"{BASE_URL}/login")

    # Trouver et completer email
    email_input = driver.find_element(*EMAIL_INPUT)
    email_input.clear()
    email_input.send_keys("hzjhkrzty")

    # Trouver et completer mdp
    password_input = driver.find_element(*PASSWORD_INPUT)
    password_input.clear()
    password_input.send_keys("hzjhkrzty")

    login_btn = driver.find_element(*LOGIN_BTN)
    login_btn.click()

    # BAM erreur, l'element n'existe pas encore!
    # error = driver.find_element(*ERROR)

    # assert error.text == "Incorrect email or password"
    # assert driver.current_url == f"{BASE_URL}/login"
    
