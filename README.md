# Feed Conveyor - Ollama AI-powered 

![alt text](/docs/structure.png)

## Description

This Telegram bot utilizes advanced AI techniques to gather, analyze, and generate content for your specific target audience (TA). By leveraging trend analysis, data extraction from multiple sources, and AI-based text generation, this bot ensures you stay on top of the latest industry trends and provide your audience with highly relevant and engaging content.

## Installation 

1. Clone the repository.
```
sudo git clone https://github.com/simadimonyan/feedconveyor.git
```
2. Uncomment and configure the `example.env` file.

```Properties
# 1. Open the example.env file.

# telegram
API_TOKEN=123456789
CHANNEL_ID=123456789
ADMINS=[123456789] #ids
CHANNEL_USERNAME=@test

# ai
OLLAMA_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_GENERATE_URL=http://host.docker.internal:11434/api/generate

# milvus 
MILVUS_PASSWORD=admin123 # default username is "root" | min password length is 5
MILVUS_HOST=http://milvus-standalone:19530

# 2. Replace the placeholder values with your own data.
# 3. Save the file as .env.
```
3. Build the project
```
sudo bash feedconveyor.sh
```

## Requirements

1. Docker 
2. Ollama 










