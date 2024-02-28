from flask import Flask, jsonify
from celerytrainer import trigger_training_pipeline
from celery.result import AsyncResult
import requests
from register import ServiceRegistrationHandler
import logging

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

class TrainService:
    def __init__(self):
        self.app = Flask(__name__)
        self.reg = ServiceRegistrationHandler("trainservice", 3000)
        self.reg.register_service()
        logging.info("Registered service")
        self.register_routes()
        logging.info("Registered routes")

    def register_routes(self):
        @self.app.route("/api/v1/triggers/<target>", methods=["POST"])
        def train(self, target):
            try:
                logger.info("Sending req to data service")
                service_info = requests.get("http://service-discovery:8000/discover/dataservice").json()
                dataservice_ip = service_info.get("name")
                dataservice_port = service_info.get("port")

                dataservice_url = f"http://{dataservice_ip}:{dataservice_port}/api/v1/{target}/full"

                r = requests.get(dataservice_url)
                
                logger.info(f"Data service response: {r.status_code}")
                data = r.json()
                
                task = trigger_training_pipeline.apply_async(args=[data, target])
                logger.info(f"Training task triggered for {task.id}")
                return jsonify({"taskId": task.id, "status": "Processing"})

            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/v1/results/<task_id>", methods=["GET"])
        def get_results(self, task_id):
            try:
                result = AsyncResult(task_id)
                logger.info(f"Successfuly received status for {task_id}")
                
                if result.ready():
                    return jsonify({"taskId": task_id, "status": "Completed", "result": result.get()})
                else:
                    return jsonify({"taskId": task_id, "status": "Processing"})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

    def run(self):
        self.app.run(debug=True)

