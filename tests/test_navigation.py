from selenium import webdriver

def test_page_de_connexion_s_ouvre():
    driver = webdriver.Chrome()

    driver.get("http://localhost:5173/login")

    assert driver.current_url == "http://localhost:5173/login"

    driver.quit()
