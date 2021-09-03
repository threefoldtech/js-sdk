from tests.frontend.pages.base import Base
from urllib.parse import urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from gevent import sleep
from tests.frontend.pages.pools.pools import Pools


class PoolsSolution(Base):
    def __init__(self, driver, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        # test
        self.driver = driver
        self.endpoint = "/admin/#/solutions/pools"

    def load(self):
        url = urljoin(self.base_url, self.endpoint)
        self.driver.get(url)

    def create(self, wallet_name, name, farm, cu=1, su=1, ips=1, duration_unit="Day", time_to_live=1):
        # switch driver to ifram
        self.wait(self.driver, "v-progress-linear__buffer")

        iframe = self.driver.find_elements_by_tag_name("iframe")[0]
        self.driver.switch_to_frame(iframe)
        self.wait(self.driver, "progressbar")

        # set pool name in input element
        self.wait(self.driver, "v-progress-circular")
        chat_box = self.driver.find_element_by_class_name("chat")
        name_element = chat_box.find_element_by_class_name("v-text-field__slot")
        name_input = name_element.find_element_by_tag_name("input")
        name_input.send_keys(name)
        self.click_button(self.driver, "NEXT")

        # set cu, su and time to live to input elements
        self._set_pool_details(cu=cu, su=su, ips=ips, duration_unit=duration_unit, time_to_live=time_to_live)

        # select the Freefarm
        farm_box = self.driver.find_element_by_class_name("v-select__selections")
        farm_input = farm_box.find_element_by_tag_name("input")
        farm_input.send_keys(farm)
        self.click_button(self.driver, "NEXT")
        self.wait(self.driver, "v-progress-circular")

        # select the wallet
        self._select_wallet(wallet_name)

        self.wait(self.driver, "v-progress-circular")
        self.wait(self.driver, "progressbar")
        self.click_button(self.driver, "FINISH")

    def extend(self, wallet_name, name, cu=1, su=1, ips=1, duration_unit="Day", time_to_live=1):
        self.wait(self.driver, "v-progress-linear__buffer")

        # select the pool and click extend
        test_pools = Pools(self.driver)
        test_pools.load()
        row = test_pools.select_pool(name)
        extend_button = row.find_element_by_tag_name("button")
        extend_button.click()

        self.wait(self.driver, "v-progress-circular")
        self.wait(self.driver, "progressbar")

        # switch driver to ifram
        iframe = self.driver.find_elements_by_tag_name("iframe")[0]
        self.driver.switch_to_frame(iframe)

        # set cu, su and time to live to input elements
        self._set_pool_details(cu=cu, su=su, ips=ips, duration_unit=duration_unit, time_to_live=time_to_live)

        # select the wallet
        self._select_wallet(wallet_name)

        self.wait(self.driver, "v-progress-circular")
        self.wait(self.driver, "progressbar")
        self.click_button(self.driver, "FINISH")

    def _select_create_extend(self, option):
        """ this function used to select create or extend pool """

        iframe = self.driver.find_elements_by_tag_name("iframe")[0]
        self.driver.switch_to_frame(iframe)
        self.wait(self.driver, "progressbar")
        chat_box = self.driver.find_element_by_class_name("chat")
        radios = chat_box.find_elements_by_class_name("v-radio")
        create_radio = [radio for radio in radios if radio.text == option][0]
        create_radio.click()
        self.click_button(self.driver, "NEXT")

        self.wait(self.driver, "v-progress-circular")

    def _set_pool_details(self, cu=1, su=1, ips=1, duration_unit="Day", time_to_live=1):
        pool_details = {
            "Required Amount of Compute Unit (CU)": cu,
            "Required Amount of Storage Unit (SU)": su,
            "Required Amount of Public IP Unit (IPv4U)": ips,
            "Please choose the duration unit": duration_unit,
            "Please specify the pools time-to-live": time_to_live,
        }
        input_form = self.driver.find_element_by_class_name("v-form")
        div = input_form.find_element_by_class_name("mb-4")
        inputs_elements = div.find_elements_by_xpath("following-sibling::div")
        for input_element in inputs_elements:
            text = input_element.find_element_by_class_name("mb-4").text
            if text in pool_details.keys():
                input = input_element.find_element_by_tag_name("input")
                input.send_keys(pool_details[text])

        self.click_button(self.driver, "NEXT")

        self.wait(self.driver, "v-progress-circular")

    def _select_wallet(self, wallet_name):
        chat_box = self.driver.find_element_by_class_name("chat")
        wallets_box = chat_box.find_element_by_class_name("v-input__slot")
        wallets = wallets_box.find_elements_by_class_name("v-radio")
        wallet = [wallet for wallet in wallets if wallet.text == wallet_name][0]
        wallet.click()

        self.click_button(self.driver, "NEXT")
