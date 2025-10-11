from flask import Flask, request, jsonify
from flask_cors import CORS
from executor.code_executor import execute_python_code, execute_cpp_code, execute_js_code
import json, os, logging
from functools import lru_cache
import re

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# -------------------------------
# Конфигурация
# -------------------------------
class Config:
    MAX_CODE_SIZE = 100000  # 100KB
    MAX_TEST_CASES = 50
    DEFAULT_TIME_LIMIT = 2
    DEFAULT_MEMORY_LIMIT = 256  # MB
    SUPPORTED_LANGUAGES = ["py", "cpp", "js"]
    EXECUTION_TIMEOUT = 10  # seconds

# -------------------------------
# Language runner mapping
# -------------------------------
RUNTIME_MAP = {
    "py": execute_python_code,
    "cpp": execute_cpp_code,
    "js": execute_js_code,
}

# -------------------------------
# Вспомогательные функции
# -------------------------------
def validate_code_size(code):
    """Проверка размера кода"""
    if len(code) > Config.MAX_CODE_SIZE:
        return False, f"Code too large. Max {Config.MAX_CODE_SIZE} characters allowed."
    return True, ""

def sanitize_input(data):
    """Базовая санитизация входных данных"""
    if isinstance(data, str):
        # Удаляем потенциально опасные символы
        data = re.sub(r'[^\x20-\x7E\n\t]', '', data)
    return data

def format_api_response(data=None, error=None, status_code=200):
    """Стандартизированный формат ответа API"""
    response = {
        "success": error is None,
        "timestamp": os.times().elapsed,
    }
    
    if error:
        response["error"] = error
    if data:
        response["data"] = data
        
    return jsonify(response), status_code

# -------------------------------
# Normal run endpoints
# -------------------------------
@app.route("/run/<lang>", methods=["POST"])
def run_code(lang):
    logger.info(f"Code execution request for language: {lang}")
    
    try:
        data = request.get_json(silent=True)
        if not data:
            return format_api_response(error="No JSON data provided", status_code=400)
        
        
        if "code" not in data:
            return format_api_response(error="No code provided", status_code=400)
            
        code = data.get("code", "")
        is_valid, size_error = validate_code_size(code)
        if not is_valid:
            return format_api_response(error=size_error, status_code=400)

        if lang not in RUNTIME_MAP:
            return format_api_response(error=f"Language {lang} not supported. Supported: {', '.join(Config.SUPPORTED_LANGUAGES)}", status_code=400)

        
        sanitized_data = {
            "code": sanitize_input(code),
            "input": sanitize_input(data.get("input", ""))
        }

        
        runner = RUNTIME_MAP[lang]
        result = runner(json.dumps(sanitized_data))

        if result.get("error") == "Time Limit Exceeded":
            return format_api_response(data=result, status_code=408)
        elif result.get("error"):
            logger.warning(f"Execution error for {lang}: {result.get('error')}")
            return format_api_response(data=result, status_code=422)  
        
        logger.info(f"Code executed successfully for {lang}")
        return format_api_response(data=result)

    except Exception as e:
        logger.error(f"Unexpected error in run_code: {str(e)}")
        return format_api_response(error="Internal server error", status_code=500)

# -------------------------------
# Task submission endpoint
# -------------------------------
@app.route("/task-submission", methods=["POST"])
def task_submission():
    """
    Expects JSON:
    {
        "code": "...",
        "lang": "py|cpp|js",
        "test_cases": [
            {"input": "1 2\n", "expected": "3\n"},
            {"input": "5 10\n", "expected": "15\n"}
        ],
        "time_limit": 2,    # seconds
        "memory_limit": 256 # MB
    }
    """
    logger.info("Task submission request received")
    
    try:
        data = request.get_json(silent=True)
        if not data:
            return format_api_response(error="No submission data provided", status_code=400)

        code = data.get("code", "").strip()
        lang = data.get("lang", "").strip()
        test_cases = data.get("test_cases", [])
        
        if not code:
            return format_api_response(error="Missing code", status_code=400)
        if not lang:
            return format_api_response(error="Missing language", status_code=400)
        if not test_cases:
            return format_api_response(error="Missing test cases", status_code=400)

        is_valid, size_error = validate_code_size(code)
        if not is_valid:
            return format_api_response(error=size_error, status_code=400)
            
        if len(test_cases) > Config.MAX_TEST_CASES:
            return format_api_response(error=f"Too many test cases. Max {Config.MAX_TEST_CASES} allowed.", status_code=400)

        if lang not in RUNTIME_MAP:
            return format_api_response(error=f"Language {lang} not supported", status_code=400)

        time_limit = float(data.get("time_limit", Config.DEFAULT_TIME_LIMIT))
        memory_limit = float(data.get("memory_limit", Config.DEFAULT_MEMORY_LIMIT))
        decimal_places = int(data.get("decimal_places", 2))

        runner = RUNTIME_MAP[lang]
        results = []
        all_passed = True

        for idx, case in enumerate(test_cases):
            payload = {
                "code": sanitize_input(code),
                "input": sanitize_input(case.get("input", ""))
            }
            
            result = runner(json.dumps(payload))
            user_out = result.get("output", "").strip()
            expected_out = case.get("expected", "").strip()
            resources = result.get("resources", {})
            verdict = "Accepted"
            validator_result = None

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
            elif user_out != expected_out:
                if data.get('validator_code'):
                    validator_payload = { 
                        "code": data['validator_code'], 
                        "input": f"{expected_out}\n{user_out}" 
                    }
                    validator_result = execute_cpp_code(json.dumps(validator_payload))
                    
                    try:
                        is_correct = bool(int(validator_result.get("output", "0").strip()))
                        verdict = "Accepted" if is_correct else "Wrong Answer"
                        if not is_correct:
                            all_passed = False
                    except ValueError:
                        verdict = "Wrong Answer"
                        all_passed = False
                elif data.get('decimal_places') is not None:
                    try:
                        user_float = round(float(user_out), decimal_places)
                        expected_float = round(float(expected_out), decimal_places)
                        verdict = "Accepted" if user_float == expected_float else "Wrong Answer"
                        if verdict == "Wrong Answer":
                            all_passed = False
                    except ValueError:
                        verdict = "Wrong Answer"
                        all_passed = False
                else:
                    verdict = "Wrong Answer"
                    all_passed = False

            results.append({
                "test_case": idx + 1,
                "input": case["input"],
                "expected": expected_out,
                "user_output": user_out,
                "status": verdict,
                "resources": resources,
                "validator_result": validator_result
            })

        overall_result = {
            "overall": "Accepted" if all_passed else "Failed",
            "total_tests": len(test_cases),
            "passed_tests": sum(1 for r in results if r["status"] == "Accepted"),
            "details": results
        }
        
        logger.info(f"Task submission completed: {overall_result['overall']}")
        return format_api_response(data=overall_result)

    except Exception as e:
        logger.error(f"Unexpected error in task_submission: {str(e)}")
        return format_api_response(error="Internal server error during task submission", status_code=500)

# -------------------------------
# Health check endpoint
# -------------------------------
@app.route("/health", methods=["GET"])
def health_check():
    """Проверка состояния сервера"""
    health_status = {
        "status": "healthy",
        "timestamp": os.times().elapsed,
        "supported_languages": Config.SUPPORTED_LANGUAGES,
        "features": {
            "code_execution": True,
            "task_submission": True,
            "multi_language": True
        }
    }
    return format_api_response(data=health_status)

@app.route("/", methods=["GET"])
def index():
    return "Code Execution API is running."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    
    logger.info(f"Starting server on port {port}, debug: {debug}")
    app.run(host="0.0.0.0", port=port, debug=debug)