const fs = require('fs');
const { spawn } = require('child_process');
const os = require('os');
const path = require('path');

let inputData = '';

process.stdin.on('data', chunk => {
    inputData += chunk;
});

process.stdin.on('end', () => {
    const response = {
        output: "",
        error: null,
        exit_code: 0,
        resources: {}
    };

    try {
        const data = JSON.parse(inputData);
        const code = data.code || '';

        // Save code to temp file
        const codeFilePath = path.join(os.tmpdir(), `code_${Date.now()}.js`);
        fs.writeFileSync(codeFilePath, code);

        // Run code and measure resources
        const child = spawn('/usr/bin/time', [
            '-f', 'USED_TIME=%U;SYS_TIME=%S;ELAPSED=%E;MEM_KB=%M',
            'node', codeFilePath
        ], { stdio: ['ignore', 'pipe', 'pipe'] }); // ignore stdin

        let stdout = '';
        let stderr = '';

        child.stdout.on('data', data => { stdout += data.toString(); });
        child.stderr.on('data', data => { stderr += data.toString(); });

        child.on('close', code => {
            response.exit_code = code;
            response.output = stdout.trim();

            const stderrLines = stderr.trim().split('\n');
            const resourceLine = stderrLines.pop(); // last line is resource info
            if (resourceLine && resourceLine.includes('USED_TIME')) {
                resourceLine.split(';').forEach(part => {
                    const [key, val] = part.split('=');
                    if (key && val) response.resources[key] = val;
                });
            }

            // If there were any errors printed before resources
            if (stderrLines.length) {
                response.error = stderrLines.join('\n');
            }

            fs.unlinkSync(codeFilePath);
            console.log(JSON.stringify(response));
        });

    } catch (e) {
        response.error = e.message;
        console.log(JSON.stringify(response));
    }
});
