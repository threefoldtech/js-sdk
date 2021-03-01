from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Base:
    base_url = "https://localhost"

    def __init__(self, *args, **kwargs):
        pass

    def wait(self, driver, class_name):
        wait = WebDriverWait(driver, 360)
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, class_name)))

    def click_button(self, driver, text):
        self.wait(driver, "progressbar")
        buttons = driver.find_elements_by_class_name("v-btn")
        next_button = [button for button in buttons if button.text == text][0]
        next_button.click()
