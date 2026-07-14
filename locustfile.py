from locust import HttpUser, task, between

class SanctionsSearchUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def search_sanctions(self):
        self.client.get('/api/sanctions/search?name=Abu Abbas')