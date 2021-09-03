from random import choice
from urllib.parse import urljoin
from tests.frontend.pages.base import Base
from selenium.webdriver.common.keys import Keys
from gevent import sleep


class Packages(Base):
    def __init__(self, driver, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.driver = driver
        self.endpoint = "/admin/#/packages"

    def load(self):
        url = urljoin(self.base_url, self.endpoint)
        self.driver.get(url)

    def add_package_if_not_added(self, package, git_url):
        installed_packages, available_packages = self.get_installed_and_available_packages()
        if package not in installed_packages.keys():
            git_url = git_url
            self.add_package(git_url=git_url)
        installed_packages, available_packages = self.get_installed_and_available_packages()
        package_card = installed_packages[package]
        return package_card

    def get_system_packages(self):
        system_packages = {}
        packages_category = self.driver.find_elements_by_class_name("row")
        system_packages_cards = packages_category[0].find_elements_by_class_name("v-card")

        for system_card in system_packages_cards:
            system_packages_cards_name = system_card.find_element_by_class_name("v-card__title")
            system_package_name = system_packages_cards_name.text
            system_packages[system_package_name] = system_card
        return system_packages

    def add_package(self, git_url=None, path=None):
        self.click_button(self.driver, "ADD")
        add_new_package_box = self.driver.find_elements_by_class_name("v-text-field__slot")
        path_input = add_new_package_box[0].find_element_by_tag_name("input")
        git_url_input = add_new_package_box[1].find_element_by_tag_name("input")

        if git_url is not None:
            git_url_input.send_keys(git_url)
            self.click_button(self.driver, "SUBMIT")
            self.wait(self.driver, "v-dialog")
            self.wait(self.driver, "v-card__progress")
        else:
            # Clear git_url_input box
            git_url_input.send_keys(Keys.CONTROL + "a")
            git_url_input.send_keys(Keys.DELETE)
            path_input.send_keys(path)
            self.click_button(self.driver, "SUBMIT")
            self.wait(self.driver, "v-dialog")
            self.wait(self.driver, "v-card__progress")

    def get_installed_and_available_packages(self):
        self.wait(self.driver, "progressbar")
        # TODO search for better solution to wait till the packages loaded
        sleep(20)
        installed_packages = {}
        available_packages = {}
        packages_category = self.driver.find_elements_by_class_name("row")
        installed_packages_cards = packages_category[1].find_elements_by_class_name("v-card")
        available_packages_cards = packages_category[2].find_elements_by_class_name("v-card")
        self.wait(self.driver, "progressbar")
        for installed_card in installed_packages_cards:
            installed_package_card_name = installed_card.find_element_by_class_name("v-card__title")
            installed_package_name = installed_package_card_name.text
            installed_packages[installed_package_name] = installed_card
        self.wait(self.driver, "progressbar")

        for available_card in available_packages_cards:
            available_package_card_name = available_card.find_element_by_class_name("v-card__title")
            available_package_name = available_package_card_name.text
            available_packages[available_package_name] = available_card

        return installed_packages, available_packages

    def delete_package(self, package_name):
        installed_packages, available_packages = self.get_installed_and_available_packages()
        if package_name in installed_packages.keys():
            package_card = installed_packages[package_name]
            delete_icon = package_card.find_element_by_class_name("v-btn")
            delete_icon.click()
            self.click_button(self.driver, "SUBMIT")
            self.wait(self.driver, "v-card__progress")

    def install_random_package(self):
        installed_packages, available_packages = self.get_installed_and_available_packages()
        random_package = choice(list(available_packages.keys()))
        package_card = available_packages[random_package]
        install_icon = package_card.find_element_by_class_name("v-btn__content")
        install_icon.click()
        self.wait(self.driver, "progressbar")
        return random_package

    def open_in_browser(self, package, git_url):
        package_card = self.add_package_if_not_added(package, git_url)
        open_in_browser = package_card.find_elements_by_class_name("v-btn__content")[1]
        open_in_browser.click()

        try:
            self.click_button(self.driver, "AGREE")
            self.wait(self.driver, "progressbar")
        except:
            pass

        return self.driver.current_url

    def chatflows(self, package, git_url):
        package_card = self.add_package_if_not_added(package, git_url)
        chatflows = package_card.find_elements_by_class_name("v-btn__content")[2]
        chatflows.click()
        cards = self.driver.find_elements_by_class_name("v-card__title")
        cards_name = []
        for card in cards:
            cards_name.append(card.text)
        return cards_name
