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

RUN python3 -m ensurepip \
    && pip3 install --upgrade pip setuptools \
    && rm -r /usr/lib/python*/ensurepip && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

RUN git clone -b dev https://github.com/Randi356/Vegeta-Userbot /root/userbot
RUN mkdir /root/userbot/.bin
RUN pip install --upgrade pip setuptools
WORKDIR /root/userbot

#Install python requirements
RUN pip3 install -r https://raw.githubusercontent.com/Randi356/Vegeta-Userbot/Vegeta-Userbot/requirements.txt

RUN pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U

EXPOSE 80 443

CMD ["python3", "-m", "userbot"]
