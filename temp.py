from datetime import datetime
import subprocess
import json
import os

def run_code(code, extension, stdInput, stdOutput):
    file_name = f'{datetime.today().strftime('%Y%m%dT%H%M%S%fZ')}'
    # file_name = 'test'

    # Save the code to a temporary file
    with open(f'{file_name}.{extension}', 'w') as f:
        f.write(code)
    
    # Execute the code with the given input
    process = 0
    
    match extension:
        case 'py':
            process = subprocess.Popen(['python', f'{file_name}.{extension}'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        case 'js':
            process = subprocess.Popen(['node', f'{file_name}.{extension}'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        case 'java':
            process = subprocess.Popen(['javac', f'{file_name}.{extension}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.communicate()
            process = subprocess.Popen(['java', f'{file_name}'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        case 'cpp':
            process = subprocess.Popen(['g++', f'{file_name}.{extension}', '-o', f'{file_name}.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.communicate()
            process = subprocess.Popen([f'./{file_name}.exe'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        case _:
            return 'Unsupported file type'
    # process = subprocess.Popen(['python', f'{file_name}.{extension}'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate(input = stdInput.encode())
    output = output.decode('utf-8').strip()
    error = error.decode('utf-8').strip()

    # Delete the temporary files

    os.remove(f'{file_name}.{extension}')
    if extension == 'java' or extension == 'cpp':
        os.remove(f'{file_name}.exe')

    return {"result": output == stdOutput, "error": error}
