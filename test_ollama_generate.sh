#!/bin/bash

echo "Ollama Chat Interface"
echo "Type 'exit' to quit"
echo "===================="

# Initialize conversation history
conversation=""

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
    
    # Add user message to conversation history
    if [ -z "$conversation" ]; then
        conversation="$user_message"
    else
        conversation="$conversation\n\nUser: $user_message"
    fi
    
    echo "Assistant: "
    
    # Send conversation history to Ollama API and parse response
    response=$(curl -s -X POST http://localhost:11434/api/generate \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"huihui_ai/qwen3-abliterated:latest\",
            \"prompt\": \"$conversation\",
            \"stream\": false
        }")
    
    # Display the complete response from the model
    echo "Complete API Response:"
    echo "$response"
    echo ""
    echo "---"
    echo ""
    
    # Extract the response text from JSON for conversation history
    if command -v jq >/dev/null 2>&1; then
        # Use jq if available for better JSON parsing
        full_response=$(echo "$response" | jq -r '.response')
    else
        # Fallback to grep/sed for basic parsing
        full_response=$(echo "$response" | grep -o '"response":"[^"]*"' | sed 's/"response":"//;s/"$//')
    fi
    
    # Extract text after \n\u003c/think\u003e\n\n if it exists
    if echo "$full_response" | grep -q "\\n\\u003c/think\\u003e\\n\\n"; then
        assistant_response=$(echo "$full_response" | sed 's/.*\\n\\u003c\/think\\u003e\\n\\n//')
    else
        assistant_response="$full_response"
    fi
    
    # Display the extracted response (after \n\u003c/think\u003e\n\n)
    echo "Extracted Response (after \\n\\u003c/think\\u003e\\n\\n):"
    echo "$assistant_response"
    echo ""
    
    # Add assistant response to conversation history
    conversation="$conversation\n\nAssistant: $assistant_response"
    
    echo ""
done
