import logging

from flask import Flask, jsonify, request

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
services = {}

        

@app.route("/register", methods=["POST"])
def register_service():
    data = request.json
    service_name = data.get("name")
    service_host = data.get("host")
    service_port = data.get("port")

    if not (service_name and service_host and service_port):
        return jsonify({"error": "Invalid data provided"}), 400

    services[service_name] = {
        "host": service_host,
        "port": service_port,
        "name": service_name,
    }
    logger.info(f"Registered new service {service_name}:{service_port}")
    return jsonify(
        {"message": f"Service {service_name} registered successfully"}
    )

@app.route("/discover/<service_name>", methods=["GET"])
def discover_service(service_name):
    service = services.get(service_name)
    if service:
        logger.info(f"Retreived info {service}")
        return jsonify(
            {
                "host": service["host"],
                "port": service["port"],
                "name": service["name"],
            }
        )
    else:
        return jsonify({"error": f"Service {service_name} not found"}), 404

   


