FROM debian:buster

RUN apt-get update && \
    apt-get install --quiet -y curl virtualenv python3 gcc libffi-dev libssl-dev python3-dev make git \
                               systemd systemd-sysv \
			       openssh-server
RUN curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
RUN curl -L "https://github.com/docker/compose/releases/download/1.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose

ENV REQUESTS_CA_BUNDLE /etc/ssl/certs

WORKDIR /opt
RUN virtualenv --python=python3 venv
ENV PATH="/opt/venv/bin:${PATH}"
