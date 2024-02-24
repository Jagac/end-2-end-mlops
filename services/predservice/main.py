from celery.result import AsyncResult
from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from celery import Celery

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="redis://localhost:6379/1",
)

app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/1')
app.autodiscover_tasks(['tasks'])


@limiter.limit("10 per minute")
@app.route("/api/v1/predictions", methods=["POST"])
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

        if fuel_type == "euro95":
            task = predict_eu95.apply_async(args=[data], queue='eu95_queue')
            task_type = "euro95"

        elif fuel_type == "diesel":
            task = predict_diesel.apply_async(args=[data], queue='diesel_queue')
            task_type = "diesel"

        elif fuel_type == "lpg":
            task = predict_lpg.apply_async(args=[data], queue='lpg_queue')
            task_type = "lpg"

        return jsonify(
            {"task_id": task.id, "task_type": task_type, "status": "Processing"}
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@limiter.limit("10 per minute")
@app.route("/api/v1/predictions/<task_type>/<task_id>", methods=["GET"])
def get_result(task_type, task_id):
    try:
        if task_type == "euro95":
            task = AsyncResult(task_id, app=predict_eu95)
        elif task_type == "diesel":
            task = AsyncResult(task_id, app=predict_diesel)
        elif task_type == "lpg":
            task = AsyncResult(task_id, app=predict_lpg)
        else:
            return jsonify({"error": "Invalid task type"}), 400

        if task.state == "SUCCESS":
            return jsonify({"task_id": task_id, "result": task.get()}), 200
        elif task.state == "FAILURE":
            return jsonify({"error": "Task failed"}), 500
        else:
            return jsonify({"status": task.state}), 202

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
