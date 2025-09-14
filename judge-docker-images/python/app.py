from flask import Flask, request, jsonify
import subprocess, json

app = Flask(__name__)

@app.route("/run", methods=["POST"])
def run_code():
    data = request.get_json()
    code = data.get("code", "")
    test_input = data.get("input", "")

    try:
        result = subprocess.run(
            ["python3", "runner.py", code, test_input],
            text=True,
            capture_output=True,
            timeout=10
        )

        if result.returncode != 0 and not result.stdout:
            return jsonify({"error": result.stderr.strip()}), 400

        return jsonify(json.loads(result.stdout.strip()))

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Time Limit Exceeded"}), 408
    except Exception as e:
        return jsonify({"error": f"Execution Error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
