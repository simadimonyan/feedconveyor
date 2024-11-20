#!/bin/bash

# Function to check if Docker is installed
is_docker_installed() {
    command -v docker > /dev/null 2>&1
}

# Function to check if Ollama is installed
is_ollama_installed() {
    command -v ollama > /dev/null 2>&1
}

# Function to check if Ollama is already running on port 11434
is_ollama_running() {
    lsof -i :11434 > /dev/null 2>&1
}

# Function to download LLAMA3 model
download_llama3() {
    echo "🔴 Retrieve LLAMA3 model..."
    ollama pull llama3.1:8b

    # Check if the command was successful
    if [ $? -eq 0 ]; then
        echo "🟢 Done!"
    else
        echo "Error downloading LLAMA3 model. Retrying..."
        download_llama3
    fi
}

# Check if Docker is installed
if ! is_docker_installed; then
    echo "🔴 Docker is not installed. Please install Docker from https://www.docker.com/get-started"
    exit 1
fi

# Check if Ollama is installed
if ! is_ollama_installed; then
    echo "🔴 Ollama is not installed. Please install Ollama from https://ollama.com"
    exit 1
fi

# Check if Ollama is already running on port 11434
if is_ollama_running; then
    echo "🟡 Ollama is already running on port 11434."
else
    # Start Ollama in the background without logging
    ollama serve --port 11434 > /dev/null 2>&1 &
    # Record Process ID.
    pid=$!

    # Pause for Ollama to start.
    sleep 5

    # Call the function to download the model
    download_llama3
fi

# Main service
sudo docker-compose up -d

# Function to display a spinning cursor
spin() {
    local delay=0.1
    local spinner=( '|' '/' '-' '\' )
    local end=$((SECONDS+10))

    while [ $SECONDS -lt $end ]; do
        for i in "${spinner[@]}"; do
            echo -ne "\r 🟡 $i Waiting main to start..."
            sleep $delay
        done
    done
}

# Call the spin function
spin

DOCKERFILE_PATH="./src/database/Dockerfile"

# Build the Docker image
sudo docker build -f $DOCKERFILE_PATH -t settings-image .

# Run the Docker container
sudo docker run --rm --name settings-container --network feed-conveyor_local-network settings-image


# Show Docker logs
sudo docker-compose logs -f

