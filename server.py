from flask import Flask, request, jsonify
from flask_cors import CORS
import temp
import subprocess
import tempfile
import json
import os

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
        stdInput = data['input']
        stdOutput = data['output']

        output = temp.run_code(data['code'], 'cpp', stdInput, stdOutput)

        return jsonify({'message': 'Success!', 'data': data, 'stdout': f'{output}'})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
