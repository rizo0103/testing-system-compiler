from flask import Flask, request, jsonify
from flask_cors import CORS
import temp
from resources import functions

app = Flask(__name__)
CORS(app)  # Разрешаем все источники

@app.route('/', methods=['GET'])
def hello():
    return jsonify({"message": "Hello, World!"}), 200

@app.route('/run', methods=['POST'])
def run_code():
    try:
        data = request.json
        code = data['code']
        ext = data['ext']
        validatorCode = data['outputValidatorCode'] if 'outputValidatorCode' in data else None
        output = data['output']
        additional_data = {
            "input": data['input'] if 'input' in data else None,
            "memory_limit": int(data['memoryLimit']),
            "time_limit": int(data['timeLimit']),
        }
        compile_output = functions.compile_code(code = code, extension = ext, additional_data = additional_data)
        # if compile_output['error'] != "No errors":
        #     return jsonify({'message': 'Compilation error', 'error': compile_output['error']}), 500
        
        if functions.compare_results(expected_output = output, user_output = compile_output['output'], precision = data['precision'] if 'precision' in data else None, validatorCode = validatorCode, input = additional_data['input'] if 'input' in additional_data else None):
            return compile_output, 200
        else:
            compile_output['status'] = "Failed"
            compile_output['error'] = "Wrong answer"
            return compile_output, 200

        # return jsonify({'message': 'Success!', 'data': data, 'output': output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/compile', methods=['POST'])
def compile_code():
    try:
        data = request.json
        
        additional_data = {
            "input": data['input'] if 'input' in data else None,
            "memory_limit": int(512),
            "time_limit": int(5),
        }
        output = functions.compile_code(data['code'], data['ext'], additional_data)

        return jsonify({'message': 'Success!', 'data': data, 'output': output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
