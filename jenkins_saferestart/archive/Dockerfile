# docker build -t python:3.7.8-jenkins-saferestart-v.0.0.1 .
# docker run --network=host --hostname $HOSTNAME -d --name jenkins_saferestart --rm -v /opt/jenkins_saferestart:/opt python:3.7.8-jenkins-saferestart-v.0.0.1

FROM python:3.7.8
RUN apt-get update \
    && apt-get install -y jq wget zip unzip dnsutils telnet
RUN wget https://github.com/ericchiang/pup/releases/download/v0.4.0/pup_v0.4.0_linux_amd64.zip \
    && unzip pup_v0.4.0_linux_amd64.zip -d /usr/local/bin
COPY requirement.txt . 

# install dependencies to the local user directory (eg. /root/.local)
RUN pip install --user -r requirement.txt

# update PATH 
ENV PATH=/root/.local:$PATH

# make sure you include the -u flag to have our stdout logged
ENTRYPOINT [ "python", "-u", "/opt/jenkins_saferestart.py" ]
