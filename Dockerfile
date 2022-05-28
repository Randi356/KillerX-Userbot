# create docker image build
FROM rendyprojects/vegeta-userbot:dev

# credit my owner @FFmpegNotInstalled
# from hub.docker.com
# don't remove credit fuck :)

RUN git clone -b Vegeta-Userbot https://github.com/Randi356/Vegeta-Userbot /root/userbot
RUN mkdir /root/userbot/.bin
RUN pip install --upgrade pip setuptools
WORKDIR /root/userbot

#Install python requirements
RUN pip3 install -r https://raw.githubusercontent.com/Randi356/Vegeta-Userbot/Vegeta-Userbot/requirements.txt

EXPOSE 80 443

CMD ["bash", "start"]
