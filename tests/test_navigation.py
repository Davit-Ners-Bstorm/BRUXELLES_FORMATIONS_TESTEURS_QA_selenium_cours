from tests.config import BASE_URL
from selenium.webdriver.common.by import By


# LOCATORS
EMAIL = (By.CSS_SELECTOR, "input[type=email")
PRIMARY_BTN = (By.CSS_SELECTOR, ".btn-primary")
INPUT_MDP = (By.XPATH, "//label[normalize-space()='Mot de passe']/following-sibling::input")
EVENEMENT_LINK = (By.PARTIAL_LINK_TEXT, "Evenements")
BTN_CONNEXION_NAVBAR = (By.PARTIAL_LINK_TEXT, "Connexion")

# Dans un monde parfait, vous avez des attributs speciaux laisser pas les gentils devs pour retrouver les elements direct
# TEST_ID = (By.CSS_SELECTOR, 'input[data-testId=test1]')

def test_page_de_connexion_s_ouvre(driver):
    driver.get(f"{BASE_URL}/login")

    assert driver.current_url == f"{BASE_URL}/login"
    assert driver.title == "eventflow"

def test_page_de_catalogue_s_ouvre(driver):
    driver.get(f"{BASE_URL}/")

    assert driver.current_url == f"{BASE_URL}/"
    assert driver.title == "eventflow"

def test_login_element(driver):
    driver.get(f"{BASE_URL}/login")

    input_email = driver.find_element(*EMAIL)
    btns = driver.find_elements(*PRIMARY_BTN)

    assert btns
    # ==
    assert len(btns) > 0



# EXO vite fait
# .click()
# => lancer test depuis page d'accueil, trouver btn connexion, cliquer dessus, et verifier que la page d'arriver c'est bien la page du login

def test_catalogue_to_login(driver):
    driver.get(BASE_URL)
    btn_connexion = driver.find_element(*BTN_CONNEXION_NAVBAR)

    btn_connexion.click()

    assert driver.current_url == f"{BASE_URL}/login"

def test_remplir_email_login(driver):
    driver.get(f"{BASE_URL}/login")
    input_email = driver.find_element(*EMAIL)

    input_email.clear()

    input_email.send_keys("admin@test")

    assert input_email.get_attribute("value") == "admin@test"


