from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from register import ServiceRegistrationHandler
from tasks.factory import TaskFactory
from tasks.params import global_variables
import logging

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class PredictionApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.reg = ServiceRegistrationHandler("predservice", 8080)
        self.reg.register_service()
        logger.info("Registered service")
        self.limiter = Limiter(
            get_remote_address,
            app=self.app,
            storage_uri="redis://localhost:6379/1",
        )
        self.register_routes()
        logger.info("Registered routes")

    def register_routes(self):
        # Apply limiter to routes using limiter.limit decorator
        # @self.limiter.limit("10 per minute")
        @self.app.route("/api/v1/predictions", methods=["POST"])
        def predict():
            try:
                data = request.json
                fuel_type = data.get("fuel_type")

                if fuel_type is None or fuel_type not in ["euro95", "diesel", "lpg"]:
                    return (
                        jsonify(
                            {
                                "error": "Invalid fuel type. Choose one of euro95, diesel, or lpg."
                            }
                        ),
                        400,
                    )

                task = (
                    TaskFactory()
                    .fuel_task(fuel_type)
                    .apply_async(args=[data], queue=f"{fuel_type}_queue")
                )
                logger.info(f"Provided data for {task.id}")
                return jsonify(
                    {"task_id": task.id, "task_type": fuel_type, "status": "Processing"}
                )

            except Exception as e:
                return jsonify({"error": str(e)}), 500

        # @self.limiter.limit("10 per minute")
        @self.app.route("/api/v1/predictions/<fuel_type>/<task_id>", methods=["GET"])
        def get_result(fuel_type: str, task_id: str) -> dict:
            try:
                task = TaskFactory().fuel_task(fuel_type)
                task_instance = task.AsyncResult(task_id)
                logger.info(f"Successfully retreived info for {task_id}")

                if task_instance.state == "SUCCESS":
                    return (
                        jsonify({"task_id": task_id, "result": task_instance.get()}),
                        200,
                    )

                elif task_instance.state == "FAILURE":
                    return jsonify({"error": "Task failed"}), 500
                else:
                    return jsonify({"status": task_instance.state}), 202
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/v1/parameters")
        def currently_running_params():
            provided_key = request.args.get("key")
            expected_key = "params"

            if provided_key != expected_key:
                return jsonify({"error": "Unauthorized"}), 401

            logger.info("Provided params to request")
            return jsonify(global_variables)

    def run(self):
        self.app.run(debug=True)
