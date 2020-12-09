from jumpscale.loader import j
from urllib.parse import urljoin
from tests.frontend.pages.base import Base
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from solutions_automation.dashboard_solutions.network import NetworkDeployAutomated


class workloads(Base):
    def __init__(self, driver, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.driver = driver
        self.endpoint = "/admin/#/workloads"

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

    def select_workload_by_ID(self, workload_ID):
        # Select workloads by ID.
        search_ID_box = self.driver.find_element_by_class_name("v-text-field__slot")
        input_search_ID = search_ID_box.find_element_by_tag_name("input")
        input_search_ID.send_keys(workload_ID)

        # Check Box wth all selected workload
        ID = self.driver.find_elements_by_class_name("v-data-table__checkbox")
        click_ID = ID[1].find_element_by_class_name("v-icon")
        click_ID.click()

    def create_workload(self, workload_name):
        test_network = NetworkDeployAutomated(
            solution_name=workload_name,
            type="Create",
            ip_version="IPv4",
            ip_select="Choose ip range for me",
            ip_range="",
            access_node="choose_random",
            pool="choose_random",
            debug=True,
        )

        test_network_dict = test_network.config
        return int(test_network_dict.get("ids")[0])

    def delete_selected_workloads(self, workload_ID):

        self.select_workload_by_ID(workload_ID)

        # Delete all selected workloads
        self.click_button("DELETE SELECTED")

        # Click confirm
        self.click_button("CONFIRM")

    def check_selected_workloads_status(self, workload_ID):

        self.driver.refresh()
        self.select_workload_by_ID(workload_ID)
        return self.driver.find_elements_by_class_name("text-start")[10].text
