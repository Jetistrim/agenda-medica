from __future__ import annotations

from flask import Flask, jsonify, request

from mock_api.data import APPOINTMENTS

app = Flask(__name__)


@app.get("/appointments")
def get_appointments():
    mode = request.args.get("mode", "ok")

    if mode == "empty":
        return jsonify([]), 200

    if mode == "invalid":
        return jsonify({"unexpected": "payload"}), 200

    return jsonify(APPOINTMENTS), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
