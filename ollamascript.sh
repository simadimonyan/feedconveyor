#!/bin/bash

# Start Ollama in the background.
ollama serve &
# Record Process ID.
pid=$!

# Pause for Ollama to start.
sleep 5

# Function to download LLAMA3 model
download_llama3() {
    echo "🔴 Retrieve LLAMA3 model..."
    ollama run llama3.1:70b
    
    # Check if the command was successful
    if [ $? -eq 0 ]; then
        echo "🟢 Done!"
    else
        echo "Error downloading LLAMA3 model. Retrying..."
        download_llama3
    fi
}

# Call the function to download the model
download_llama3

# Wait for Ollama process to finish.
wait $pid
