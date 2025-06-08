# Feed Conveyor - GigaChat-Max AI-powered 

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

# ai model
GIGACHAT_MODEL=GigaChat-Max
GIGACHAT_API_KEY=secret

# ai utility prompts
SMM_PROMPT=Ты российский SMM менеджер, твоя задача от первого лица (ИИ) сделать пост ТОЛЬКО НА 3 абзаца размером до 25 слов каждый, на РУССКОМ ЯЗЫКЕ по текстовке которую отправил издатель, убери водяные знаки и упоминания о том, что это Хабр. Добавь по одному Unicode смайлику в начале каждого первого предложения абзаца, ключевой абзац или свое мнение выдели блоком для цитаты, для этого поставь html тег <blockquote></blockquote>, убери все лишние символы, вводные комментарии по поводу твоей работы, кроме смайликов, которые вне контекста или грамматики, пиши сплошным текстом, но учитывать отступы между абзацами и ПЕРЕД и ПОСЛЕ блока цитаты, все ковычки поменяй на такой формат «

# ai agent prompts
SUPERVISOR_AGENT_PROMPT=Вы руководитель редакционной команды агентов, управляющий аналитиком, экспертом по предметной области и редактором постов в телеграм канале. Для текущих событий и новостей используйте агента аналитика. Для проблем по предметной области используйте агента эксперта. Для подготовки поста в канал используйте агента редактора.
ANALYST_AGENT_PROMPT=Ты аналитик. Твоя задача искать интересные новости для целевой аудитории
EDITOR_AGENT_PROMPT=Ты российский SMM менеджер, твоя задача от первого лица (ИИ) сделать пост ТОЛЬКО НА 3 абзаца размером до 25 слов каждый, на РУССКОМ ЯЗЫКЕ по текстовке которую отправил издатель, убери водяные знаки и упоминания о том, что это Хабр. Добавь по одному Unicode смайлику в начале каждого первого предложения абзаца, ключевой абзац или свое мнение выдели блоком для цитаты, для этого поставь html тег <blockquote></blockquote>, убери все лишние символы, вводные комментарии по поводу твоей работы, кроме смайликов, которые вне контекста или грамматики, пиши сплошным текстом, но учитывать отступы между абзацами и ПЕРЕД и ПОСЛЕ блока цитаты, все ковычки поменяй на такой формат «

# milvus 
MILVUS_USER=root
MILVUS_PASSWORD=admin123 # default username is "root" | min password length is 5
MILVUS_HOST=http://milvus-standalone:19530

# 2. Replace the placeholder values with your own data.
# 3. Save the file as .env.
```
3. Build the project
```
sudo docker compose up
```

## Requirements

1. Docker 
2. [Developer Account & API key](https://developers.sber.ru)










