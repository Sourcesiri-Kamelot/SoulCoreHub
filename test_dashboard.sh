#!/bin/bash

# Test SoulCore Dashboard functionality
echo "Testing SoulCore Dashboard functionality..."

# Test the server connection
echo "Testing server connection..."
RESPONSE=$(curl -s -X POST http://localhost:3000/execute-command -H "Content-Type: application/json" -d '{"command":"echo Dashboard connection test successful"}')

if [[ $RESPONSE == *"successful"* ]]; then
  echo "✅ Server connection test passed"
else
  echo "❌ Server connection test failed"
  echo "Response: $RESPONSE"
fi

# Test agent response hub
echo "Testing agent response hub..."
python3 -c "import os; os.makedirs('logs/agent_queries', exist_ok=True)"
python3 agent_response_hub.py anima "Test query" > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "✅ Agent response hub test passed"
else
  echo "❌ Agent response hub test failed"
fi

# Test PsyNet integration
echo "Testing PsyNet integration..."
python3 -c "from psynet_integration import PsyNetIntegration; psynet = PsyNetIntegration()" > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "✅ PsyNet integration test passed"
else
  echo "❌ PsyNet integration test failed"
fi

# Test custom prediction script
echo "Testing custom prediction script..."
python3 custom_prediction.py general "Test prediction" 7 > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "✅ Custom prediction script test passed"
else
  echo "❌ Custom prediction script test failed"
fi

echo "All tests completed!"
echo "You can now run ./update_dashboard.sh to update the dashboard with the fixed version."
