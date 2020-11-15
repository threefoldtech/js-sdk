from urllib.parse import urljoin
from tests.frontend.pages.base import Base
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Packages(Base):
    def __init__(self, driver, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.driver = driver
        self.endpoint = "/admin/#/packages"

    def load(self):
        url = urljoin(self.base_url, self.endpoint)
        self.driver.get(url)

    def system_packages(self):
        packages = self.driver.find_elements_by_class_name("v-card__title")
        system_packages = []
        for i in range(6):
            system_packages.append(packages[i].text)
        return system_packages

    def add_package(self, git_url):
        buttons = self.driver.find_elements_by_class_name("v-btn")
        add_button = [button for button in buttons if button.text == "ADD"][0]
        add_button.click()
        add_new_package_box = self.driver.find_elements_by_class_name("v-text-field__slot")
        git_url_input = add_new_package_box[1].find_element_by_tag_name("input")
        git_url_input.send_keys(git_url)
        buttons = self.driver.find_elements_by_class_name("v-btn")
        submit_button = [button for button in buttons if button.text == "SUBMIT"][0]
        submit_button.click()
        wait = WebDriverWait(self.driver, 60)
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "v-dialog")))

    def check_package_card(self):

        installed_packages = {}
        available_packages = {}
        packages_category = self.driver.find_elements_by_class_name("row")
        installed_packages_cards = packages_category[1].find_elements_by_class_name("v-card")
        available_packages_cards = packages_category[2].find_elements_by_class_name("v-card")
        for installed_card in installed_packages_cards:
            installed_package_card_name = installed_card.find_element_by_class_name("v-card__title")
            installed_name = installed_package_card_name.text
            installed_packages[installed_name] = installed_card

        for available_card in available_packages_cards:
            available_package_card_name = available_card.find_element_by_class_name("v-card__title")
            available_name = available_package_card_name.text
            available_packages[available_name] = available_card

        return installed_packages, available_packages

    def delete_package(self, package_name):
        installed_packages, available_packages = self.check_package_card()
        for package in installed_packages.keys():
            if package == package_name:
                package_card = installed_packages[package_name]
                delete_icon = package_card.find_element_by_class_name("v-btn")
                delete_icon.click()
                break
        else:
            return
        buttons = self.driver.find_elements_by_class_name("v-btn")
        submit_button = [button for button in buttons if button.text == "SUBMIT"][0]
        submit_button.click()
