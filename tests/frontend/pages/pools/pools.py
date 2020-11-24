from tests.frontend.pages.base import Base
from urllib.parse import urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Pools(Base):
    def __init__(self, driver, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.driver = driver
        self.endpoint = "/admin/#/pools"

    def load(self):
        url = urljoin(self.base_url, self.endpoint)
        self.driver.get(url)

    def list(self):
        self.wait("v-progress-linear__buffer")
        table_box = self.driver.find_element_by_class_name("v-data-table")
        table = table_box.find_element_by_tag_name("table")
        rows = table.find_elements_by_tag_name("tr")
        return [
            (row.text.split()[1], float(row.text.split()[4]), float(row.text.split()[5]))
            for row in rows
            if row.text.split()[4] != "Compute"
        ]

    def hide_pool(self, name):
        self.wait("v-progress-linear__buffer")
        table_box = self.driver.find_element_by_class_name("v-data-table")
        table = table_box.find_element_by_tag_name("table")
        rows = table.find_elements_by_tag_name("tr")
        for row in rows:
            if row.text.split()[1] == name:
                row.click()
        self.click_button("HIDE POOL")
        self.click_button("CLOSE")

    def wait(self, class_name):
        wait = WebDriverWait(self.driver, 60)
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, class_name)))

    def click_button(self, text):
        buttons = self.driver.find_elements_by_class_name("v-btn")
        next_button = [button for button in buttons if button.text == text][0]
        next_button.click()
