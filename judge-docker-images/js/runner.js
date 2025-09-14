const fs = require('fs');
const { spawn } = require('child_process');
const os = require('os');
const path = require('path');

function main() {
    let inputData = '';

    process.stdin.on('data', chunk => inputData += chunk);

    process.stdin.on('end', () => {
        try {
            const data = JSON.parse(inputData);
            const code = data.code || '';
            const userInput = data.input || '';

            const codeFile = path.join(os.tmpdir(), `code_${Date.now()}.js`);
            fs.writeFileSync(codeFile, code);

            const child = spawn('/usr/bin/time', [
                '-f', 'USED_TIME=%U;SYS_TIME=%S;ELAPSED=%E;MEM_KB=%M',
                'node', codeFile
            ], { stdio: ['pipe', 'pipe', 'pipe'] });

            // Pipe user input if exists
            if (userInput) child.stdin.write(userInput);
            child.stdin.end();

            let stdout = '';
            let stderr = '';

            child.stdout.on('data', data => stdout += data.toString());
            child.stderr.on('data', data => stderr += data.toString());

            child.on('close', code => {
                fs.unlinkSync(codeFile);

                const lines = stderr.trim().split('\n');
                const resourceLine = lines.pop();
                const programStderr = lines.join('\n');

                const resources = {};
                if (resourceLine && resourceLine.includes('USED_TIME')) {
                    resourceLine.split(';').forEach(part => {
                        const [key, val] = part.split('=');
                        if (key && val) resources[key] = val;
                    });
                }

                const outputJson = {
                    output: stdout.trim(),
                    error: programStderr || null,
                    exit_code: code,
                    resources
                };

                console.log(JSON.stringify(outputJson));
            });

        } catch (err) {
            console.log(JSON.stringify({
                output: '',
                error: `Execution Error: ${err.message}`,
                exit_code: -1,
                resources: {}
            }));
        }
    });
}

main();
