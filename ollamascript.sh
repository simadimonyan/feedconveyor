#!/bin/bash

# Function to download LLAMA3.1 model
download_llama3() {
    echo "🔴 Retrieve LLAMA3 model..."
    /bin/ollama run llama3.1:70b
    
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
