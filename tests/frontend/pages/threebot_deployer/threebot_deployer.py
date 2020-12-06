from jumpscale.loader import j
from urllib.parse import urljoin
from tests.frontend.pages.base import Base
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ThreebotDeployer(Base):
    def __init__(self, driver, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.driver = driver
        self.endpoint = "threebot_deployer"

    def load(self):
        url = urljoin(self.base_url, self.endpoint)
        self.driver.get(url)

    def wait(self, class_name):
        wait = WebDriverWait(self.driver, 60)
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, class_name)))

    def view_an_existing_3bot_button(self):
        view_my_existing_3bot_button = self.driver.find_elements_by_class_name("v-btn__content")[2]
        view_my_existing_3bot_button.click()

    def switch_driver_to_iframe(self):
        # switch driver to iframe
        self.wait("v-progress-linear__buffer")
        iframe = self.driver.find_elements_by_tag_name("iframe")[0]
        self.driver.switch_to_frame(iframe)

    def click_button(self, text):
        buttons = self.driver.find_elements_by_class_name("v-btn")
        next_button = [button for button in buttons if button.text == text][0]
        next_button.click()

    def find_correct_3bot_instance(self, action, my_3bot_instance_name):
        # Find correct 3bot instance row
        self.wait("v-progress-linear__buffer")
        table_box = self.driver.find_element_by_class_name("v-data-table")
        table = table_box.find_element_by_tag_name("table")
        rows = table.find_elements_by_tag_name("tr")

        if action == "delete":
            i = 2
        else:
            i = 0
        for row in rows:
            if row.text.split()[0] == my_3bot_instance_name:
                row.find_elements_by_class_name("v-btn__content")[i].click()
                break
            else:
                return

    def payment_process(self, wallet_name):
        chat_box = self.driver.find_element_by_class_name("chat")
        payment = chat_box.find_elements_by_tag_name("mb-4").text
        payment_info = payment.splitlines()
        destination_wallet_address = payment_info[3]
        currency = payment_info[5]
        reservation_ID = payment_info[7]
        total_amount = payment_info[9].split()[0]

        a = getattr(j.clients.stellar, wallet_name).get_asset(currency)
        j.clients.stellar.demos_wallet.transfer(
            destination_wallet_address, amount=total_amount, memo_text=reservation_ID, asset=f"{a.code}:{a.issuer}"
        )

    def deploy_new_3bot(self, my_3bot_instances, password, wallet_name):
        # Deploy a new 3bot button
        deploy_new_3bot_button = self.driver.find_elements_by_class_name("v-btn__content")[1]
        deploy_new_3bot_button.click()

        self.wait("v-progress-linear__buffer")

        # switch driver to iframe
        iframe = self.driver.find_elements_by_tag_name("iframe")[0]
        self.driver.switch_to_frame(iframe)

        # Create a new 3Bot instance
        chat_box = self.driver.find_element_by_class_name("chat")
        create_button = chat_box.find_elements_by_class_name("v-input--selection-controls__ripple")[0]
        create_button.click()

        self.click_button("NEXT")

        # ThreeBot instance Name
        name_element = chat_box.find_element_by_class_name("v-text-field__slot")
        name_input = name_element.find_element_by_tag_name("input")
        name_input.send_keys(my_3bot_instances)

        self.click_button("NEXT")

        self.wait("progressbar")
        self.wait("progressbar")

        # Choose how much resources the deployed solution will use.
        # We use 1 CPU, 2GB Memory, and 2GB[SSD] in this example.
        instance_resources = chat_box.find_elements_by_class_name("v-radio")[0]
        instance_resources.click()

        self.click_button("NEXT")
        self.click_button("NEXT")

        # Threebot recovery password
        password_element = chat_box.find_element_by_class_name("v-text-field__slot")
        password_input = password_element.find_element_by_tag_name("input")
        password_input.send_keys(password)

        self.click_button("NEXT")

        self.wait("v-progress-circular")

        # The deployment location policy ( We here use it automatically )
        instance_location_selection = chat_box.find_elements_by_class_name("v-radio")[0]
        instance_location_selection.click()

        self.click_button("NEXT")
        self.wait("v-progress-circular")
        self.click_button("NEXT")

        self.wait("v-progress-circular")

        self.click_button("NEXT")

        # Payment process
        self.payment_process(wallet_name=wallet_name)

        self.click_button("NEXT")
        self.wait("v-progress-circular")
        self.click_button("NEXT")
        self.wait("progressbar")

        # Threebot instance URL
        threebot_instance_chat_box = self.driver.find_element_by_class_name("chat")
        threebot_instance_URL = threebot_instance_chat_box.find_element_by_class_name("v-card__text").text.split()[14]

        self.click_button("FINISH")
        return threebot_instance_URL

    def view_my_3bot(self, status):

        # View an existing 3bot button
        self.view_an_existing_3bot_button()

        self.wait("progressbar")

        # Select 3bot instances with certain status
        my_3bot_box = self.driver.find_element_by_class_name("v-select__selections")
        status_input = my_3bot_box.find_element_by_tag_name("input")
        status_input.send_keys(status)

        # List 3bot instances
        self.wait("v-progress-linear__buffer")
        table_box = self.driver.find_element_by_class_name("v-data-table")
        table = table_box.find_element_by_tag_name("table")
        rows = table.find_elements_by_tag_name("tr")

        my_3bot_instances = []
        for row in rows:
            my_3bot_instance = row.text.split()[0]
            my_3bot_instances.append(my_3bot_instance)

        return my_3bot_instances

    def delete_threebot_instance(self, my_3bot_instance_name, password):

        # View an existing 3bot button
        self.view_an_existing_3bot_button()

        # Find correct 3bot instance row
        self.find_correct_3bot_instance("delete", my_3bot_instance_name=my_3bot_instance_name)

        # Destroy 3bot box
        destroy_3bot = self.driver.find_element_by_class_name("v-card")
        input_password = destroy_3bot.find_element_by_tag_name("input")
        input_password.send_keys(password)

        # Click CONFIRM button
        self.click_button("CONFIRM")

        self.wait("v-progress-linear__buffer")

    def start_stopped_3bot_instance(self, my_3bot_instance_name, password, wallet_name):

        # View an existing 3bot button
        self.view_an_existing_3bot_button()

        # Find correct 3bot instance row
        self.find_correct_3bot_instance("start", my_3bot_instance_name=my_3bot_instance_name)

        # switch driver to iframe
        self.switch_driver_to_iframe()

        password_chat_box = self.driver.find_element_by_class_name("chat")
        input_password = password_chat_box.find_element_by_tag_name("input")
        input_password.send_keys(password)

        self.click_button("NEXT")
        self.wait("progressbar")

        self.click_button("NEXT")
        self.payment_process(wallet_name=wallet_name)

        self.click_button("NEXT")
        self.wait("v-progress-linear__buffer")

        # Threebot instance URL
        threebot_instance_chat_box = self.driver.find_element_by_class_name("chat")
        threebot_instance_URL = threebot_instance_chat_box.find_element_by_class_name("v-card__text").text.split()[14]

        self.click_button("FINISH")
        return threebot_instance_URL

    def stop_running_3bot_instance(self, my_3bot_instance_name, password):

        # View an existing 3bot button
        self.view_an_existing_3bot_button()

        # Find correct 3bot instance row
        self.find_correct_3bot_instance("stop", my_3bot_instance_name=my_3bot_instance_name)

        password_chat_box = self.driver.find_element_by_class_name("v-card")
        input_password = password_chat_box.find_element_by_tag_name("input")
        input_password.send_keys(password)

        self.click_button("CONFIRM")
        self.wait("v-progress-linear__buffer")
