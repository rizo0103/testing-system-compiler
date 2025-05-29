import os
import time
import subprocess
import tracemalloc
import numpy as np
from datetime import datetime

def compare_floats(num1, num2, precision=2):
    """
    Compare two floating-point numbers with a specified precision.
    
    Args:
        num1 (float): The first number to compare.
        num2 (float): The second number to compare.
        precision (int): The number of decimal places to consider for comparison.
    
    Returns:
        bool: True if the numbers are equal up to the specified precision, False otherwise.
    """
    return round(num1, precision) == round(num2, precision)

def compile_code(code, extension, additional_data = None):
    """
    Compile the given code and return the result.
    
    Args:
        code (str): The code to compile.
        extension (str): The extension of the code file.
        additional_data (object): Input Cases, Time Limit, Memory Limit (optional)
    
    Returns:
        success (bool): The compilation status.
        output (str): The output of the compilation process.
        error (str): The error message if any.
        compileTime (float): The time taken for compilation.
        memoryUsage (float): The memory usage during compilation
    """
    file_name_base = 'resources/' + datetime.today().strftime("%Y%m%dT%H%M%S%fZ")
    source_file = f'{file_name_base}.{extension}'
    executable_file = file_name_base + '.exe'
    compile_output = ""
    compile_error = "No errors"
    compile_success = True
    compile_time = 0
    compile_memory_usage = 0
    process = 0

    try:
        # Сохраняем код во временный файл
        with open(source_file, 'w') as f:
            f.write(code)

        tracemalloc.start()
        start_time = time.time()

        match extension:
            case 'java':
                if additional_data['input']:
                    process = subprocess.Popen(['java', source_file], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    process = subprocess.Popen(['javac', source_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if process.returncode != 0:
                    compile_success = False
            case 'cpp':
                process = subprocess.Popen(['g++', source_file, '-o', executable_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                _, compile_error = process.communicate()
                if process.returncode != 0:
                    compile_success = False
                else:
                    if additional_data['input']:
                        process = subprocess.Popen([executable_file], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    else:
                        process = subprocess.Popen([executable_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            case 'py':
                if 'input' in additional_data:
                    process = subprocess.Popen(['python', source_file], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    process = subprocess.Popen(['python', source_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
            case 'js':
                process = subprocess.Popen(['node', source_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            case _:
                compile_success = False
                compile_error = 'Unsupported file type for compilation'

        start_time = time.time()
        compile_output, compile_error = process.communicate(input = additional_data['input'].encode())
        compile_output = compile_output.decode('utf-8').strip()
        compile_error = compile_error.decode('utf-8').strip()
        compile_time = time.time() - start_time
        current, peak = tracemalloc.get_traced_memory()
        compile_memory_usage = peak / (1024 * 1024) if peak > 0 else 0
        
    finally:
        tracemalloc.stop()
        # Удаляем временный исходный файл
        if os.path.exists(source_file):
            os.remove(source_file)
            os.remove(executable_file) if executable_file and os.path.exists(executable_file) else None

    if "MemoryError" in compile_error:
        compile_error = "MemoryError"
        compile_success = False
    
    if "TimeoutError" in compile_error:
        compile_error = "TimeoutError"
        compile_success = False
    
    if 'time_limit' in additional_data and additional_data['time_limit'] < compile_time:
        compile_error = "TimeLimitExceeded"
        compile_success = False
    
    if 'memory_limit' in additional_data and additional_data['memory_limit'] < compile_memory_usage:
        compile_error = "MemoryLimitExceeded"
        compile_success = False

    return {
        "status": "Passed" if compile_success else "Failed",
        "output": compile_output,
        "error": compile_error,
        "compileTime": round(compile_time, 5),
        "memoryUsage": round(compile_memory_usage, 5),
    }

def compare_results(expected_output, user_output, precision = None, validatorCode = None, input = None):
    """
    Compare expected code output with user's output.

    Args:
        expected_output (str): correct output,
        user_output (str): user's output
        precision (int, optional): number of decimal places to round to.

    Returns:
        bool: True if outputs match, else False.
    """
    try:

        if validatorCode is not None:
            expected_output = input + '\n' + expected_output if input else expected_output
            user_output = input + '\n' + user_output if input else user_output
            additional_data = {
                "input": expected_output,
            }

            expected_result = compile_code(validatorCode, 'cpp', additional_data)
            additional_data = {
                "input": user_output,
            }
            user_result = compile_code(validatorCode, 'cpp', additional_data)
                        
            return expected_result['output'] == user_result['output']

        expected_tokens = expected_output.strip().split()
        user_tokens = user_output.strip().split()
        
        if len(expected_tokens) != len(user_tokens):
            return False


        # Пробуем преобразовать в числа (если это возможно)
        try:
            expected_array = np.array(expected_tokens, dtype=float)
            user_array = np.array(user_tokens, dtype=float)

            if precision is not None:
                expected_array = np.round(expected_array, precision)
                user_array = np.round(user_array, precision)

            return np.array_equal(expected_array, user_array)

        except ValueError:
            # Если это не числа, сравниваем как строки
            return expected_tokens == user_tokens

    except:
        try:
            expected_float = float(expected_output)
            user_float = float(user_output)
            return compare_floats(expected_float, user_float, precision=precision)
        except:
            return False
