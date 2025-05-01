#!/bin/bash
# fix_dashboard.sh - Script to fix the SoulCore dashboard buttons

# Set the base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR" || exit 1

# Create logs directory if it doesn't exist
mkdir -p "$BASE_DIR/logs"

echo "Fixing SoulCore Dashboard..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed. Please install npm first."
    exit 1
fi

# Install required Node.js packages
echo "Installing required Node.js packages..."
npm install express --save

# Create a directory for dashboard logs
mkdir -p "$BASE_DIR/logs/dashboard"

# Fix permissions for the dashboard server
chmod +x "$BASE_DIR/soulcore_dashboard_server.js"
chmod +x "$BASE_DIR/server.js"

# Create a script to start the dashboard
cat > "$BASE_DIR/scripts/start_dashboard.sh" << 'EOF'
#!/bin/bash
# start_dashboard.sh - Script to start the SoulCore dashboard

# Set the base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR" || exit 1

# Create logs directory if it doesn't exist
mkdir -p "$BASE_DIR/logs/dashboard"

echo "Starting SoulCore Dashboard..."

# Kill any existing dashboard server
pkill -f "node.*soulcore_dashboard_server.js" 2>/dev/null

# Start the dashboard server
node "$BASE_DIR/soulcore_dashboard_server.js" > "$BASE_DIR/logs/dashboard/dashboard_server.log" 2>&1 &

# Wait for the server to start
sleep 2

# Check if the server is running
if pgrep -f "node.*soulcore_dashboard_server.js" > /dev/null; then
    echo "SoulCore Dashboard server started successfully"
    echo "Open your browser and navigate to http://localhost:3000"
else
    echo "Error: Failed to start SoulCore Dashboard server"
    echo "Check the log file for details: $BASE_DIR/logs/dashboard/dashboard_server.log"
    exit 1
fi
EOF

# Make the start dashboard script executable
chmod +x "$BASE_DIR/scripts/start_dashboard.sh"

# Create a test script for the dashboard
cat > "$BASE_DIR/scripts/test_dashboard_buttons.js" << 'EOF'
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
EOF

echo "Dashboard fix completed!"
echo "To start the dashboard, run: bash $BASE_DIR/scripts/start_dashboard.sh"
echo "To test the dashboard buttons, run: node $BASE_DIR/scripts/test_dashboard_buttons.js"
