from tests.frontend.pages.base import Base
from urllib.parse import urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Wallets(Base):
    def __init__(self, driver, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.driver = driver
        self.endpoint = "/admin/#/wallets"

    def load(self):
        url = urljoin(self.base_url, self.endpoint)
        self.driver.get(url)

    def create(self, name):
        buttons = self.driver.find_elements_by_class_name("v-btn")
        create_button = [button for button in buttons if button.text == "CREATE"][0]
        create_button.click()
        wallet_name_box = self.driver.find_element_by_class_name("v-text-field__slot")
        wallet_name_input = wallet_name_box.find_element_by_tag_name("input")
        wallet_name_input.send_keys(name)
        buttons = self.driver.find_elements_by_class_name("v-btn")
        submit_button = [button for button in buttons if button.text == "SUBMIT"][0]
        submit_button.click()
        wait = WebDriverWait(self.driver, 60)
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "v-dialog")))

    def list(self):
        wallets = {}
        wallets_class = self.driver.find_element_by_class_name("row")
        wallets_cards = wallets_class.find_elements_by_class_name("v-card")
        for wallet_card in wallets_cards:
            wallet_card_name = wallet_card.find_element_by_class_name("v-card__title")
            wallet_name = wallet_card_name.text
            wallets[wallet_name] = wallet_card

        return wallets

    def delete(self, name):
        wallets = self.list()
        for wallet in wallets.keys():
            if wallet == name:
                wallet_card = wallets[name]
                delete_icon = wallet_card.find_element_by_class_name("v-btn")
                delete_icon.click()
                break
        else:
            return
        buttons = self.driver.find_elements_by_class_name("v-btn")
        submit_button = [button for button in buttons if button.text == "SUBMIT"][0]
        submit_button.click()
