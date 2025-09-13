const fs = require('fs');
const { spawn } = require('child_process');
const os = require('os');
const path = require('path');

let inputData = '';

process.stdin.on('data', chunk => {
    inputData += chunk;
});

process.stdin.on('end', () => {
    try {
        const data = JSON.parse(inputData);
        const code = data.code || '';
        const userInput = data.input || '';

        const codeFilePath = path.join(os.tmpdir(), `code_${Date.now()}.js`);
        fs.writeFileSync(codeFilePath, code);

        const child = spawn('/usr/bin/time', [
            '-f', 'USED_TIME=%U;SYS_TIME=%S;ELAPSED=%E;MEM_KB=%M',
            'node', codeFilePath
        ], {
            stdio: ['pipe', 'pipe', 'pipe']
        });

        // Pipe user input to the process
        if (userInput) {
            child.stdin.write(userInput);
        }
        child.stdin.end();

        let stdout = '';
        let stderr = '';

        child.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        child.stderr.on('data', (data) => {
            stderr += data.toString();
        });

        child.on('close', () => {
            fs.unlinkSync(codeFilePath);

            const stderrLines = stderr.trim().split('\n');
            const resourceLine = stderrLines.pop();
            const programStderr = stderrLines.join('\n');

            let usage = {};
            if (resourceLine && resourceLine.includes('USED_TIME')) {
                resourceLine.split(';').forEach(part => {
                    const [key, val] = part.split('=');
                    if (key && val) {
                        usage[key] = val;
                    }
                });
            }

            // Print program output first, then usage JSON
            if (stdout) process.stdout.write(stdout);
            if (programStderr) process.stderr.write(programStderr);
            
            // The last thing printed to stdout is the usage JSON
            console.log(JSON.stringify(usage));
        });

    } catch (e) {
        // If there's an error parsing the input JSON, etc.
        const usage = { error: e.message };
        console.log(JSON.stringify(usage));
    }
});