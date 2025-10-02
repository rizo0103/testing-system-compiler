from flask import Flask, request, jsonify
from flask_cors import CORS
from executor.code_executor import execute_python_code, execute_cpp_code, execute_js_code
import json, os

app = Flask(__name__)
CORS(app)

RUNTIME_MAP = {
    "py": execute_python_code,
    "cpp": execute_cpp_code,
    "js": execute_js_code,
}

@app.route("/run/<lang>", methods=["POST"])
def run_code(lang):
    data = request.json
    if not data:
        return jsonify({"error": "No code provided"}), 400

    if lang not in RUNTIME_MAP:
        return jsonify({"error": f"Language {lang} not supported"}), 400

    runner = RUNTIME_MAP[lang]
    result = runner(json.dumps(data))

    if result.get("error") == "Time Limit Exceeded":
        return jsonify(result), 408
    elif result.get("error"):  
        return jsonify(result), 500

    return jsonify(result), 200

@app.route("/task-submission", methods=["POST"])
def task_submission():
    data = request.json
    if not data:
        return jsonify({"error": "No submission data"}), 400

    code = data.get("code")
    lang = data.get("lang")
    test_cases = data.get("test_cases", [])
    time_limit = float(data.get("time_limit", 2))
    memory_limit = float(data.get("memory_limit", 256))
    validator_code = data.get("validator_code")

    if not code or not lang or not test_cases:
        return jsonify({"error": "Missing code, lang or test_cases"}), 400

    if lang not in RUNTIME_MAP:
        return jsonify({"error": f"Language {lang} not supported"}), 400

    runner = RUNTIME_MAP[lang]
    results = []
    all_passed = True

    for idx, case in enumerate(test_cases):
        payload = {
            "code": code, 
            "input": case["input"], 
            "validator_code": validator_code
        }
        if validator_code:
            payload["expected"] = case.get("expected")

        result = runner(json.dumps(payload))

        user_out = result.get("output", "").strip()
        expected_out = case.get("expected", "").strip()
        resources = result.get("resources", {})
        verdict = "Accepted"

        if result.get("error"):
            verdict = result["error"]
            all_passed = False
        elif float(resources.get("USED_TIME", 0)) > time_limit:
            verdict = "Time Limit Exceeded"
            all_passed = False
        elif float(resources.get("MEM_KB", 0)) > memory_limit * 1024:
            verdict = "Memory Limit Exceeded"
            all_passed = False
        elif result.get("exit_code", 0) != 0:
            verdict = "Runtime Error"
            all_passed = False
        elif validator_code:
            # If a validator was used, the runner provides the verdict
            verdict = result.get("verdict", "Wrong Answer")
            if verdict != "Accepted":
                all_passed = False
        elif user_out != expected_out:
            verdict = "Wrong Answer"
            all_passed = False

        results.append({
            "test_case": idx + 1,
            "input": case["input"],
            "expected": expected_out,
            "user_output": user_out,
            "status": verdict,
            "resources": resources
        })

    return jsonify({
        "overall": "Accepted" if all_passed else "Failed",
        "details": results
    })

@app.route("/", methods=["GET"])
def index():
    return "Code Execution API is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)