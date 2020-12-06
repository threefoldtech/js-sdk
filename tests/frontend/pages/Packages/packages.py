from random import choice
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

    def wait(self, class_name):
        wait = WebDriverWait(self.driver, 90)
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, class_name)))

    def click_button(self, button_type):
        buttons = self.driver.find_elements_by_class_name("v-btn")
        button = [button for button in buttons if button.text == button_type][0]
        self.wait("progressbar")
        button.click()

    def check_threebot_deployer_package(self):
        threebot_installed = 0
        installed_packages, available_packages = self.check_packages_type()
        if "threebot_deployer" not in installed_packages.keys():
            git_url = "https://github.com/threefoldtech/js-sdk/tree/development/jumpscale/packages/threebot_deployer"
            self.add_package(git_url=git_url)
            threebot_installed = 1
        installed_packages, available_packages = self.check_packages_type()
        package_card = installed_packages["threebot_deployer"]
        return package_card, threebot_installed

    def system_packages(self):
        system_packages = {}
        packages_category = self.driver.find_elements_by_class_name("row")
        system_packages_cards = packages_category[0].find_elements_by_class_name("v-card")

        for system_card in system_packages_cards:
            system_packages_cards_name = system_card.find_element_by_class_name("v-card__title")
            system_name = system_packages_cards_name.text
            system_packages[system_name] = system_card
        return system_packages

    def add_package(self, git_url=None, path=None):
        self.click_button("ADD")
        add_new_package_box = self.driver.find_elements_by_class_name("v-text-field__slot")
        path_input = add_new_package_box[0].find_element_by_tag_name("input")
        git_url_input = add_new_package_box[1].find_element_by_tag_name("input")

        if git_url is not None:
            git_url_input.send_keys(git_url)
            self.click_button("SUBMIT")
            self.wait("v-dialog")
        else:
            # Clear git_url_input box
            git_url_input.clear()
            path_input.send_keys(path)
            self.click_button("SUBMIT")
            self.wait("v-dialog")

    def check_packages_type(self):
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
        installed_packages, available_packages = self.check_packages_type()
        for package in installed_packages.keys():
            if package == package_name:
                package_card = installed_packages[package_name]
                delete_icon = package_card.find_element_by_class_name("v-btn")
                self.wait("v-btn")
                delete_icon.click()
                break
        else:
            return
        self.click_button("SUBMIT")

    def install_package(self):
        installed_packages, available_packages = self.check_packages_type()
        random_package = choice(list(available_packages.keys()))
        package_card = available_packages[random_package]
        install_icon = package_card.find_element_by_class_name("v-btn__content")
        install_icon.click()
        self.wait("progressbar")
        return random_package

    def open_in_browser(self):
        package_card, threebot_installed = self.check_threebot_deployer_package()
        open_in_browser = package_card.find_elements_by_class_name("v-btn__content")[1]
        open_in_browser.click()
        return self.driver.current_url, threebot_installed

    def chatflows(self):
        package_card, threebot_installed = self.check_threebot_deployer_package()
        chatflows = package_card.find_elements_by_class_name("v-btn__content")[2]
        chatflows.click()
        cards = self.driver.find_elements_by_class_name("v-card__title")
        cards_name = []
        for card in cards:
            cards_name.append(card.text)
        return cards_name, threebot_installed
