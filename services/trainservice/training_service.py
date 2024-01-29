from flask import Flask, jsonify, request
from celery_trainer import trigger_training_pipeline

app = Flask(__name__)

@app.route("/api/v1/trainers", methods=["POST"])
def train():
    try:
        data = request.json
        task = trigger_training_pipeline.delay(data)

        return jsonify({"task_id": task.id, "status": "Processing"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")