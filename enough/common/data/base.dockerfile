FROM debian:buster

RUN apt-get update && \
    apt-get install --quiet -y curl virtualenv python3 gcc libssl-dev python3-dev make
RUN curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh

WORKDIR /opt
RUN virtualenv --python=python3 venv
ENV PATH="/opt/venv/bin:${PATH}"
