from tests.config import BASE_URL

def test_page_de_connexion_s_ouvre(driver):
    driver.get(f"{BASE_URL}/login")

    assert driver.current_url == f"{BASE_URL}/login"
    assert driver.title == "eventflow"

def test_page_de_catalogue_s_ouvre(driver):
    driver.get(f"{BASE_URL}/")

    assert driver.current_url == f"{BASE_URL}/"
    assert driver.title == "eventflow"
