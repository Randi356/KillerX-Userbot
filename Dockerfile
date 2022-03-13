FROM python:slim-buster

# By @rencprx 

RUN git clone -b Vegeta-Userbot https://github.com/Randi356/Vegeta-Userbot /root/userbot
RUN mkdir /root/userbot/.bin
RUN pip install --upgrade pip setuptools
WORKDIR /root/userbot

#Install python requirements
RUN /bin/sh -c pip3 install -r https://raw.githubusercontent.com/Randi356/Vegeta-Userbot/Vegeta-Userbot/requirements.txt

EXPOSE 80 443

CMD ["python3", "-m", "userbot"]
