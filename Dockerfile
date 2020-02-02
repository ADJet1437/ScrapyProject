FROM ubuntu:16.04

RUN apt-get update && apt-get install -y \
    python-pip \
    python-setuptools \
    python-dev \ 
    libmysqlclient-dev \
    libxml2-dev \
    libxslt1-dev \ 
    xvfb \
    firefox \
    apache2 \
    libtiff5-dev \
    libjpeg8-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    python-tk \
    docker.io 

# TODO add default network = host
# so you will have you host networking settings, such as dns, for instance

WORKDIR /alaScrapy

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

# TODO need to share the code from local project dir with the container one

VOLUME /var/log/alaScrapy

COPY . /alaScrapy

