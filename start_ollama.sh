#!/usr/bin/env bash

export PATH="$PATH:/workspace/ollama/bin"
export OLLAMA_MODELS="/workspace/models"
export PYTHONPATH="/workspace/python_libraries"
chmod +x /workspace/ollama/bin/ollama
export OLLAMA_API_BASE="http://localhost:11434"
export OLLAMA_HOST=0.0.0.0

# Check if ollama is already running
if ! curl -s http://localhost:11434/ > /dev/null 2>&1; then
    echo "Starting ollama serve..."
    # Start ollama serve in the background
    ollama serve &

    # Wait until it’s ready
    echo "Waiting for ollama to be ready..."
    until curl -s http://localhost:11434/; do
      sleep 0.1
    done
    echo "Ollama is ready!"

    # Run curl in the background
    curl http://localhost:11434/api/generate -d '{"model": "huihui_ai/qwen3-abliterated:latest", "prompt": "Hello"}' &
else
    echo "Ollama is already running."
fi


