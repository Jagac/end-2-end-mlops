import logging
from flask import Flask, jsonify, request
from register import ServiceRegistrationHandler
from apisource import DataHandler

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
reg = ServiceRegistrationHandler("dataservice", 3000)
reg.register_service()
logger.info("Service registered")


@app.route("/api/v1/<target>/full", methods=["GET"])
def getFullData(target):
    try:
        logger.info(f"Received full data request for: {target}")
        data_handler = DataHandler(target)
        full_data, latest_date = data_handler.get_full()
        
        response_data = {
            "latestDate": latest_date,
            "data": full_data.to_dict(orient="records"),
        }
        
        ip = request.environ.get("REMOTE_ADDR")
        logger.info(f"Data successfully processed and sent to {ip}")
        return jsonify(response_data), 200
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/<target>/latest", methods=["GET"])
def getLatestData(target):
    try:
        logger.info(f"Received latest data request for: {target}")
        data_handler = DataHandler(target)
        full_data = data_handler.get_latest()
        
        response_data = {
            "data": full_data.to_dict(orient="records"),
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500
