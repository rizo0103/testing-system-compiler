// Read JS code from stdin
let code = "";
process.stdin.on("data", chunk => code += chunk);
process.stdin.on("end", () => {
    try {
        // Execute the JS code
        let result = eval(code);
        
        if (result != undefined) {
            console.log(result);
        }
    } catch (error) {
        console.error("Error:", error.toString());
    }
});