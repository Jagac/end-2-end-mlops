from flask import Flask, render_template
from tests import ModelMonitoringHandler


app = Flask(__name__)


@app.route("/", methods=["GET"])
def show_test_results():
    
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
