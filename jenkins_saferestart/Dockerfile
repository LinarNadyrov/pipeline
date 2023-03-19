# docker build -t infra.binary.alfabank.ru/jenkins-ssh-slave:1.3.5-python-jenkins-rotator .
FROM python:3.7/jenkins-ssh-slave:1.3.5-python
RUN apt-get update \
    && apt-get install -y jq wget zip \
    && wget https://github.com/ericchiang/pup/releases/download/v0.4.0/pup_v0.4.0_linux_amd64.zip \
    && unzip pup_v0.4.0_linux_amd64.zip -d /usr/local/bin
COPY requirement.txt . 
# install dependencies to the local user directory (eg. /root/.local)
USER jenkins
RUN pip3.7 install --user -r requirement.txt
# update PATH 
ENV PATH=/root/.local:$PATH
USER root