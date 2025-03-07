from flask import Flask, request, jsonify
from flask_cors import CORS
import temp

app = Flask(__name__)
CORS(app)  # Разрешаем все источники

@app.route('/', methods=['GET'])
def hello():
    return jsonify({"message": "Hello, World!"}), 200

@app.route('/run', methods=['POST'])
def run_code():
    try:
        data = request.json
        output = temp.run_code(data['code'], data['ext'], data['input'], data['output'], int(data['timeLimit']), int(data['memoryLimit']))

        return jsonify({'message': 'Success!', 'data': data, 'output': output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
