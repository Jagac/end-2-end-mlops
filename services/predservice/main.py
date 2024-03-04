import logging
from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from register import ServiceRegistrationHandler
from tasks.factory import TaskFactory
from tasks.params import global_variables

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
reg = ServiceRegistrationHandler("predservice", 8080)
reg.register_service()
logger.info("Registered service")
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="redis://localhost:6379/1",
)


@limiter.limit("10 per minute")
@app.route("/api/v1/predictions", methods=["POST"])
def predict():
    try:
        data = request.json
        fuel_type = data.get("fuelType")

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
            {"taskId": task.id, "taskType": fuel_type, "status": "processing"}
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@limiter.limit("10 per minute")
@app.route("/api/v1/predictions/<fuel_type>/<task_id>", methods=["GET"])
def getResult(fuel_type: str, task_id: str) -> dict:
    try:
        task = TaskFactory().fuel_task(fuel_type)
        task_instance = task.AsyncResult(task_id)
        logger.info(f"Successfully retreived info for {task_id}")

        if task_instance.state == "SUCCESS":
            return (
                jsonify({"taskId": task_id, "result": task_instance.get()}),
                200,
            )

        elif task_instance.state == "FAILURE":
            return jsonify({"error": "Task failed"}), 500
        else:
            return jsonify({"status": task_instance.state}), 202
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/parameters")
def currentlyRunningParams():
    provided_key = request.args.get("key")
    expected_key = "params"

    if provided_key != expected_key:
        return jsonify({"error": "Unauthorized"}), 401

    logger.info("Provided params to request")
    return jsonify(global_variables)
