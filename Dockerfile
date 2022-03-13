FROM python:slim-buster

RUN apt update && apt upgrade -y && \
    apt install --no-install-recommends -y \
        bash \
        curl \
        ffmpeg \
        gcc \
        git \
        libjpeg-dev \
        libjpeg62-turbo-dev \
        libwebp-dev \
        musl \
        musl-dev \
        atomicparsley \
        neofetch \
        rsync \
        zlib1g \
        zlib1g-dev

COPY . /tmp/userbot_local
WORKDIR /usr/src/app/Vegeta-Userbot/

RUN git clone -b dev https://github.com/Randi356/Vegeta-Userbot.git /usr/src/app/Vegeta-Userbot/
RUN rsync --ignore-existing --recursive /tmp/userbot_local/ /usr/src/app/Vegeta-Userbot/

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-warn-script-location --no-cache-dir -r requirements.txt

RUN rm -rf /var/lib/apt/lists /var/cache/apt/archives /tmp
CMD ["python3", "-m", "userbot"]
