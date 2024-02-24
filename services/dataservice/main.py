from flask import Flask, jsonify
from data import DataHandler
from register import ServiceRegistrationHandler
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

app = Flask(__name__)
reg = ServiceRegistrationHandler("dataservice", 3000)
reg.register_service()
logging.info("Registered")


@app.route("/api/v1/<target>/full", methods=["GET"])
def get_full_data(target):
    logging.info(f"received for: {target}",)
    data_handler = DataHandler(target)
    full_data = data_handler.get_full()
    return jsonify(full_data.to_dict(orient="records"))


@app.route("/api/v1/<target>/latest", methods=["GET"])
def get_latest_data(target):
    data_handler = DataHandler(target)
    full_data = data_handler.get_latest()
    return jsonify(full_data.to_dict(orient="records"))
