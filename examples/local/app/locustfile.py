from locust import HttpUser, between, task

from locust_telemetry import entrypoint

# Load core telemetry
entrypoint.initialize()


class HttpBinUser(HttpUser):
    """
    Demo Locust user hitting multiple httpbin.org endpoints.
    """

    wait_time = between(1, 3)

    @task(3)
    def get_root(self):
        # Simple GET request with query parameters
        self.client.get("/get?demo=true")

    @task(2)
    def post_data(self):
        # POST request with JSON body
        self.client.post("/post", json={"foo": "bar", "baz": 123})

    @task(1)
    def get_status(self):
        # Simulate status responses (200, 404, 500, etc.)
        self.client.get("/status/200")
        self.client.get("/status/404")
        self.client.get("/status/500")

    @task(1)
    def delayed_response(self):
        # Endpoint that waits 2 seconds before responding
        self.client.get("/delay/2")

    @task(1)
    def get_headers(self):
        # Returns request headers sent
        self.client.get("/headers")

    @task(1)
    def set_and_get_cookie(self):
        # Set a cookie, then read it back
        self.client.get("/cookies/set?locust=demo")
        self.client.get("/cookies")

    @task(1)
    def follow_redirect(self):
        # Redirect to /get
        self.client.get("/redirect-to?url=/get")

    @task(1)
    def get_image(self):
        # Fetch a PNG image (binary response)
        self.client.get("/image/png")
