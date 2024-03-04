import logging

import requests
from celery.result import AsyncResult
from celerytrainer import trigger_training_pipeline
from flask import Flask, jsonify, request
from register import ServiceRegistrationHandler

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
reg = ServiceRegistrationHandler("trainservice", 1234)
reg.register_service()
logger.info("Registered")

@app.route("/api/v1/triggers/<target>", methods=["POST"])
def train(target):
    try:
        logger.info("Requesting data service information")
        service_info = requests.get(
            "http://service-discovery:8000/discover/dataservice"
        ).json()
        dataservice_ip = service_info.get("name")
        dataservice_port = service_info.get("port")
        logger.info(f"Request sent to: {dataservice_ip}:{dataservice_port}")
        dataservice_url = (
            f"http://{dataservice_ip}:{dataservice_port}/api/v1/{target}/full"
        )

        r = requests.get(dataservice_url)
        logger.info(f"Data sevice response: {r.status_code}")
        response_data = r.json()
        data = response_data["data"]
        latest_train_date = response_data["latestDate"]

        task = trigger_training_pipeline.apply_async(args=[data, target])
        logger.info("Task sent to queue")
        
        with open("date.txt", "w") as f:
            f.write(latest_train_date)
        
        
        return jsonify({"taskId": task.id, "status": "Processing"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/results/<task_id>", methods=["GET"])
def get_results(task_id):
    try:
        result = AsyncResult(task_id)
        logger.info(f"Task result received for {task_id}")
        if result.ready():
            return jsonify(
                {"taskId": task_id, "status": "Completed", "result": result.get()}
            )
        else:
            return jsonify({"taskId": task_id, "status": "Processing"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/trainingdate", methods=["GET"])
def return_trained_date():
    try:
        with open("date.txt", "r") as f:
            trained_date = f.read().strip()
            
        return jsonify({"trainedDate": trained_date}), 200 
    
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404 