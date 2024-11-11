ARG PYTHON_VERSION=3.12.6
FROM python:${PYTHON_VERSION}-bookworm as base

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

COPY . .

CMD [ "python", "./src/bot.py" ]
