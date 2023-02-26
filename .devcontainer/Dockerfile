FROM mcr.microsoft.com/devcontainers/python:3.11

USER vscode
ENV PATH "/home/vscode/.local/bin:${PATH}"
WORKDIR /workspaces/the-war-tracker-bot

RUN sudo chown -R 1000:1000 /workspaces/the-war-tracker-bot && \
    export DEBIAN_FRONTEND=noninteractive && \
    sudo apt-get update && \
    sudo apt-get -y install curl make redis-server && \
    sudo sed -i "s/bind .*/bind 127.0.0.1/g" /etc/redis/redis.conf

RUN export PYTHONUNBUFFERED=1 && \
    curl -sSL https://install.python-poetry.org | python -
