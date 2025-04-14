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

def compile_code(code, extension, input = None):
    """
    Compile the given code and return the result.
    
    Args:
        code (str): The code to compile.
        extension (str): The extension of the code file.
        input (str): Input cases (optional)
    
    Returns:
        success (bool): The compilation status,
        output (str): The output of the compilation process,
        error (str): The error message if any,
        compileTime (float): The time taken for compilation,
        compileMemoryUsage (float): The memory usage during compilation.
    """
    file_name_base = 'resources/' + datetime.today().strftime("%Y%m%dT%H%M%S%fZ")
    source_file = f'{file_name_base}.{extension}'
    executable_file = file_name_base + '.exe'
    compile_output = ""
    compile_error = ""
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
                if input:
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
                    process = subprocess.Popen([executable_file], stdin=subprocess.PIPE if input else None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            case 'py':
                if input:
                    process = subprocess.Popen(['python', source_file], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    process = subprocess.Popen(['python', source_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
            case 'js':
                process = subprocess.Popen(['node', source_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            case _:
                compile_success = False
                compile_error = 'Unsupported file type for compilation'

        start_time = time.time()
        compile_output, compile_error = process.communicate(input = input.encode())
        # compile_output = process.stdin.write(input) if input else None
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

        # При ошибке компиляции удаляем и исполняемый файл, если он был создан
        # if os.path.exists(executable_file):
        #     os.remove(executable_file)

    return {
        "status": "Passed" if compile_success else "Failed",
        "output": compile_output,
        "error": compile_error,
        "compileTime": round(compile_time, 5),
        "memoryUsage": round(compile_memory_usage, 5),
    }

def compare_results(expected_output, user_output, precision=None):
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
