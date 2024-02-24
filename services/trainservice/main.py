from flask import Flask, jsonify, request
from celery_trainer import trigger_training_pipeline
from celery.result import AsyncResult
import requests
from register import ServiceRegistrationHandler
import logging

app = Flask(__name__)
reg = ServiceRegistrationHandler("dataservice", 3000)
reg.register_service()
logging.info("Registered")


@app.route("/api/v1/triggers/<target>", methods=["POST"])
def train(target):

    try:
        logging.info("Sending req")
        service_info = requests.get(
            "http://service-discovery:8000/discover/dataservice"
        ).json()
        dataservice_ip = service_info.get("name")
        dataservice_port = service_info.get("port")

        dataservice_url = (
            f"http://{dataservice_ip}:{dataservice_port}/api/v1/{target}/full"
        )

        data = requests.get(dataservice_url).json()

        task = trigger_training_pipeline.apply_async(args=[data, target])

        return jsonify({"task_id": task.id, "status": "Processing"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/results/<task_id>", methods=["GET"])
def get_results(task_id):
    try:
        result = AsyncResult(task_id)
        if result.ready():
            return jsonify(
                {"task_id": task_id, "status": "Completed", "result": result.get()}
            )
        else:
            return jsonify({"task_id": task_id, "status": "Processing"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
