#!/bin/bash

echo "Ollama Chat Interface (Chat API)"
echo "Type 'exit' to quit"
echo "================================"

# Check if jq is available
if ! command -v jq >/dev/null 2>&1; then
    echo "Error: jq is required for this script. Please install jq first."
    echo "On Ubuntu/Debian: sudo apt install jq"
    echo "On CentOS/RHEL: sudo yum install jq"
    exit 1
fi

# Initialize conversation history as an array of messages
messages=()

while true; do
    echo -n "You: "
    read -r user_message
    
    # Check if user wants to exit
    if [ "$user_message" = "exit" ]; then
        echo "Goodbye!"
        break
    fi
    
    # Skip empty messages
    if [ -z "$user_message" ]; then
        continue
    fi
    
    # Add user message to conversation history using jq for proper JSON formatting
    user_message_json=$(echo "$user_message" | jq -R -s '{"role": "user", "content": .}')
    messages+=("$user_message_json")
    
    echo "Assistant: "
    
    # Prepare the messages array for JSON using jq
    messages_json=$(printf '%s\n' "${messages[@]}" | jq -s .)
    
    # Create the complete request payload using jq
    request_payload=$(jq -n \
        --arg model "huihui_ai/qwen3-abliterated:latest" \
        --argjson messages "$messages_json" \
        '{
            model: $model,
            messages: $messages,
            stream: false
        }')
    
    # Send conversation history to Ollama Chat API and parse response
    response=$(curl -s -X POST http://localhost:11434/api/chat \
        -H "Content-Type: application/json" \
        -d "$request_payload")
    
    # Display the complete response from the model
    echo "Complete API Response:"
    echo "$response"
    echo ""
    echo "---"
    echo ""
    
    # Extract the response text from JSON for conversation history
    assistant_response=$(echo "$response" | jq -r '.message.content')
    
    # Add assistant response to conversation history using jq for proper JSON formatting
    assistant_message_json=$(echo "$assistant_response" | jq -R -s '{"role": "assistant", "content": .}')
    messages+=("$assistant_message_json")
    
    echo ""
done 