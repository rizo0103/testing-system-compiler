from resources import functions
from datetime import datetime

def run_code(code, extension, stdOutput, timeLimit, memoryLimit, precision=None, stdInput = None):
    compile_result = functions.compile_code(code, extension, stdInput, timeLimit, memoryLimit)

    if compile_result['status'] == False:
        return compile_result
    
    output = compile_result['output']

    print(f'output: {output}')

    compile_result = function.compare_results(stdOutput, output, precision if precision else None)
    
    # return compile_result
    # return {
    #     "status": status,
    #     "error": error,
    #     "output": output,
    #     "expectedOutput": stdOutput,
    #     "input": stdInput,
    #     "compileTime": round(compile_time, 5),  # in seconds
    #     "memoryUsage": round(memory_usage, 5), # in megabytes
    # }
def compile_code(code, extension, input):
    # print(functions.compile_code(code, extension, {"input": input, "memory_limit": 512, "time_limit": 5}))
    print (functions.compile_code(code, extension, {"input": input, "memory_limit": 512, "time_limit": 5}))
    if input != None:
        return functions.compile_code(code, extension, input)
    
    return functions.compile_code(code, extension)