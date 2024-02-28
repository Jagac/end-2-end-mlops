from flask import Flask, jsonify
from datahandler import DataHandler
from register import ServiceRegistrationHandler
import logging

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


class DataService:
    def __init__(self):
        self.app = Flask(__name__)
        self.reg = ServiceRegistrationHandler("dataservice", 3000)
        self.reg.register_service()
        logger.info("Service registered")
        self.register_routes()
        logger.info("Routes registered")

    def register_routes(self):
        @self.app.route("/api/v1/<target>/full", methods=["GET"])
        def get_full_data(target):
            logger.info(f"Received full data request for: {target}")
            data_handler = DataHandler(target)
            full_data = data_handler.get_full()
            return jsonify(full_data.to_dict(orient="records"))

        @self.app.route("/api/v1/<target>/latest", methods=["GET"])
        def get_latest_data(target):
            logger.info(f"Received latest data request for: {target}")
            data_handler = DataHandler(target)
            full_data = data_handler.get_latest()
            return jsonify(full_data.to_dict(orient="records"))

    def run(self):
        self.app.run(debug=True)
