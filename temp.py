from datetime import datetime
import tracemalloc
import subprocess
import time
import os

def run_code(code, extension, stdInput, stdOutput, timeLimit, memoryLimit):
    file_name = f'{datetime.today().strftime("%Y%m%dT%H%M%S%fZ")}'
    # file_name = 'test'

    # Save the code to a temporary file
    with open(f'{file_name}.{extension}', 'w') as f:
        f.write(code)
    
    # Execute the code with the given input
    process = 0

    # Start monitoring memory usage
    tracemalloc.start()

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

    # Get the start time of the compilation
    start_time = time.time()
    
    output, error = process.communicate(input = stdInput.encode())
    output = output.decode('utf-8').strip()
    error = error.decode('utf-8').strip()
    process.wait()

    # Get the end time of the code compilation
    end_time = time.time()

    # Calculate the time taken to compile the code and get the memory usage
    compile_time = end_time - start_time
    memory_usage = tracemalloc.get_traced_memory()

    # Convert memory usage to megabytes
    memory_usage = memory_usage[1] / (1024 * 1024)

    # Stop monitoring memory usage
    tracemalloc.stop()

    # Delete the temporary files

    os.remove(f'{file_name}.{extension}')
    if extension == 'java' or extension == 'cpp':
        os.remove(f'{file_name}.exe')

    status = "Passed"
    error = "No errors"

    if timeLimit < compile_time:
        status = "Failed"
        error = "Time limit exceeded"
    
    if memoryLimit < memory_usage:
        status = "Failed"
        error = "Memory limit exceeded"
    
    if stdOutput != output:
        status = "Failed"
        error = "Wrong output"

    return {
        "status": status,
        "error": error,
        "output": output,
        "expectedOutput": stdOutput,
        "input": stdInput,
        "compileTime": round(compile_time, 5),  # in seconds
        "memoryUsage": round(memory_usage, 5), # in megabytes
    }
