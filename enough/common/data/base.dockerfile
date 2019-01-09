FROM debian:buster

RUN apt-get update && \
    apt-get install --quiet -y curl virtualenv python2 gcc libssl-dev python-dev make
RUN curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh

WORKDIR /opt
RUN virtualenv venv
ENV PATH="/opt/venv/bin:${PATH}"
