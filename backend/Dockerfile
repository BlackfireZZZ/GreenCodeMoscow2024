# Используем официальный базовый образ для Python 3.12
FROM python:3.12-slim

# Создаем файл sources.list и заменяем зеркала на Yandex
RUN echo "deb http://mirror.yandex.ru/debian/ bookworm main contrib non-free" > /etc/apt/sources.list && \
    echo "deb http://mirror.yandex.ru/debian/ bookworm-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://mirror.yandex.ru/debian-security/ bookworm-security main contrib non-free" >> /etc/apt/sources.list

# Устанавливаем необходимые зависимости
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    xvfb \
    firefox-esr \
    --no-install-recommends

# Устанавливаем последнюю версию GeckoDriver
RUN GECKO_DRIVER_VERSION=$(curl -sS https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep 'tag_name' | cut -d '"' -f 4) && \
    wget -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/$GECKO_DRIVER_VERSION/geckodriver-$GECKO_DRIVER_VERSION-linux64.tar.gz && \
    tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin/ && \
    rm /tmp/geckodriver.tar.gz

# Устанавливаем Python зависимости
COPY backend/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

WORKDIR /backend
COPY backend/ .

# Используем ENTRYPOINT для запуска Python приложения
ENTRYPOINT ["python3", "app.py"]
