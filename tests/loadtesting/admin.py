from locust import HttpUser, task, between


class QuickstartUser(HttpUser):
    # Our class defines a wait_time function that will make the simulated users
    #  wait between 5 and 9 seconds after each task is executed
    wait_time = between(5, 9)

    @task
    def index_page(self):
        self.client.get("https://localhost/admin/#/", verify=False)

    @task
    def list_alerts(self):
        self.client.post("https://localhost/admin/actors/alerts/list_alerts", verify=False)

    @task
    def list_alerts_gedis(self):
        self.client.post("http://localhost:8000/admin/alerts/list_alerts", verify=False)
