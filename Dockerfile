# create docker image build
FROM rendyprojects/killerx-userbot:buster

# credit my owner @FFmpegNotInstalled
# from hub.docker.com
# don't remove credit fuck :)

RUN git clone -b KillerX-Userbot https://github.com/Randi356/KillerX-Userbot /root/userbot
RUN mkdir /root/userbot/.bin
RUN pip install --upgrade pip setuptools
WORKDIR /root/userbot

#Install python requirements
RUN pip3 install -r https://raw.githubusercontent.com/Randi356/KillerX-Userbot/KillerX-Userbot/requirements.txt

EXPOSE 80 443

CMD ["bash", "start"]
