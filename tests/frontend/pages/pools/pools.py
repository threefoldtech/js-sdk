from tests.frontend.pages.base import Base
from urllib.parse import urljoin
from selenium.webdriver.common.by import By


class Pools(Base):
    def __init__(self, driver, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.driver = driver
        self.endpoint = "/admin/#/pools"

    def load(self):
        url = urljoin(self.base_url, self.endpoint)
        self.driver.get(url)

    def list(self):
        self.wait(self.driver, "v-progress-linear__buffer")
        table_box = self.driver.find_element_by_class_name("v-data-table")
        table = table_box.find_element_by_tag_name("table")
        rows = table.find_elements_by_tag_name("tr")
        # the row header: ID Name Farm Expiration Compute-Units Storage-Unit ....
        # and we need to return Name(index of 1), CU(index of 4) and SU(index of 5)
        # and ignore the the header row
        return [
            (row.text.split()[1], float(row.text.split()[4]), float(row.text.split()[5]))
            for row in rows
            if row.text.split()[4] != "Compute"
        ]

    def hide_pool(self, name):
        row = self.select_pool(name)
        row.click()
        self.click_button(self.driver, "HIDE POOL")
        self.click_button(self.driver, "CLOSE")

    def select_pool(self, name):
        self.wait(self.driver, "v-progress-linear__buffer")
        table_box = self.driver.find_element_by_class_name("v-data-table")
        table = table_box.find_element_by_tag_name("table")
        rows = table.find_elements_by_tag_name("tr")
        for row in rows:
            if row.text.split()[1] == name:
                return row
