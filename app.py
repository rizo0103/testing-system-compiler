from flask import Flask, request, jsonify
from flask_cors import CORS
from executor.code_executor import execute_python_code, execute_cpp_code

app = Flask(__name__)
CORS(app)

@app.route("/run/py", methods=["POST"])
def run_python():
    code = request.json.get("code", "")
    if not code:
        return jsonify({"error": "No code provided"}), 400

    result = execute_python_code(code)
    
    if result.get("error") == "Time Limit Exceeded":
        return jsonify(result), 408
    elif "error" in result:
        return jsonify(result), 500
    
    return jsonify(result)

@app.route("/run/cpp", methods=["POST"])
def run_cpp():
    code = request.json.get("code", "")
    if not code:
        return jsonify({"error": "No code provided"}), 400

    result = execute_cpp_code(code)

    if result.get("error") == "Time Limit Exceeded":
        return jsonify(result), 408
    elif "error" in result:
        return jsonify(result), 500
    
    return jsonify(result)


@app.route("/", methods=["GET"])
def index():
    return "Code Execution API is running."

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)