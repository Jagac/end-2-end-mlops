import socket
import requests


class ServiceRegistrationHandler:
    def __init__(self, service_name, service_port) -> None:
        self.SERVICE_NAME = service_name
        self.SERVICE_PORT = service_port
        self.SERVICE_HOST = self.get_host_ip()
        self.SERVICE_DISCOVERY_URL = "http://service-discovery:8000/register"

    def register_service(self):
        payload = {
            "name": self.SERVICE_NAME,
            "host": self.SERVICE_HOST,
            "port": self.SERVICE_PORT,
        }
        try:
            response = requests.post(self.SERVICE_DISCOVERY_URL, json=payload)
            response.raise_for_status()
            print(f"Service {self.SERVICE_NAME} registered successfully")
        except Exception as e:
            print(f"Failed to register service {self.SERVICE_NAME}: {e}")

    def get_host_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            host_ip = s.getsockname()[0]
            s.close()

            return host_ip
        except Exception as e:
            print(f"Error occurred while getting host IP: {e}")
            return None
