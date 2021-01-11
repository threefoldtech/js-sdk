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

    def add_funded(self, name):
        # get funded wallet button and click
        buttons = self.driver.find_elements_by_class_name("v-btn")
        add_funded_button = [button for button in buttons if button.text == "ADD TESTNET FUNDED WALLET"][0]
        add_funded_button.click()
        # set the wallet name in name input element
        wallet_name_box = self.driver.find_element_by_class_name("v-text-field__slot")
        wallet_name_input = wallet_name_box.find_element_by_tag_name("input")
        wallet_name_input.send_keys(name)
        # get submit button and click
        buttons = self.driver.find_elements_by_class_name("v-btn")
        submit_button = [button for button in buttons if button.text == "SUBMIT"][0]
        submit_button.click()
        # wait until the creation is finished
        wait = WebDriverWait(self.driver, 60)
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "v-dialog")))

    def import_(self, name, secret, network):
        # get the import button and click
        buttons = self.driver.find_elements_by_class_name("v-btn")
        import_button = [button for button in buttons if button.text == "IMPORT"][0]
        import_button.click()
        # get the wallet details and loop through input elements and set (name, secret, network)
        wallet_details_box = self.driver.find_elements_by_class_name("v-input")
        input_boxes = {"Name": name, "Secret": secret, "Network": network}
        for box in wallet_details_box:
            if box.text in input_boxes.keys():
                box.find_element_by_tag_name("input").send_keys(input_boxes[box.text])
        # get the submit button and click
        buttons = self.driver.find_elements_by_class_name("v-btn")
        submit_button = [button for button in buttons if button.text == "SUBMIT"][0]
        submit_button.click()
        # wait until the importing is finished
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

    def get_secret(self, name):
        wallets = self.list()
        if name in wallets.keys():
            # get the wallet card end click to show wallet details
            wallet_card = wallets[name]
            wallet_card.click()
            # click on the show secret button
            wallet_details = self.driver.find_element_by_class_name("v-data-table")
            secret_input_box = wallet_details.find_element_by_class_name("v-input__slot")
            button = secret_input_box.find_element_by_tag_name("button")
            button.click()
            # get the value of secret
            secret_input = secret_input_box.find_element_by_tag_name("input")
            secret = secret_input.get_attribute("value")
            buttons = self.driver.find_elements_by_class_name("v-btn")
            close_button = [button for button in buttons if button.text == "CLOSE"][0]
            close_button.click()
            return secret

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

    def get_balance(self, name):
        wallets = self.list()
        if name in wallets.keys():
            wallet_card = wallets[name]
            wallet_card.click()
            wallet_details = self.driver.find_element_by_class_name("v-data-table")
            # get spams that contain balances and check that there are spams elements
            balances_row = wallet_details.find_elements_by_class_name("v-chip__content")
            if len(balances_row) >= 2:
                balances = [balances_row[0].text, balances_row[1].text]
                buttons = self.driver.find_elements_by_class_name("v-btn")
            else:
                balances = []
            close_button = [button for button in buttons if button.text == "CLOSE"][0]
            close_button.click()
            return balances
