// test_dashboard_buttons.js - Script to test the SoulCore dashboard buttons

const http = require('http');

// Function to test a command
function testCommand(command) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'localhost',
            port: 3000,
            path: '/execute-command',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        };

        const req = http.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => {
                data += chunk;
            });
            res.on('end', () => {
                try {
                    const result = JSON.parse(data);
                    resolve(result);
                } catch (e) {
                    reject(e);
                }
            });
        });

        req.on('error', (error) => {
            reject(error);
        });

        req.write(JSON.stringify({ command }));
        req.end();
    });
}

// Test a simple command
async function runTest() {
    try {
        console.log('Testing dashboard button functionality...');
        const result = await testCommand('echo "Dashboard button test successful"');
        console.log('Test result:', result);
        console.log('Dashboard buttons are working correctly!');
    } catch (error) {
        console.error('Test failed:', error);
        console.error('Dashboard buttons are not working correctly.');
    }
}

// Run the test
runTest();
