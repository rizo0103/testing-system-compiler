from resources import functions
from datetime import datetime
import tracemalloc
import subprocess
import time
import os

def run_code(code, extension, stdInput, stdOutput, timeLimit, memoryLimit, precision=None):
    compile_result = functions.compile_code(code, extension, stdInput)
    return compile_result
    # return {
    #     "status": status,
    #     "error": error,
    #     "output": output,
    #     "expectedOutput": stdOutput,
    #     "input": stdInput,
    #     "compileTime": round(compile_time, 5),  # in seconds
    #     "memoryUsage": round(memory_usage, 5), # in megabytes
    # }
def compile_code(code, extension, input = None):
    return functions.compile_code(code, extension, input)