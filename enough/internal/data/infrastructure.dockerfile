FROM debian:stretch

RUN apt-get update && \
    apt-get install --quiet -y sudo curl python systemd systemd-sysv openssh-server

RUN curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
RUN curl -L "https://github.com/docker/compose/releases/download/1.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose

ENV REQUESTS_CA_BUNDLE /etc/ssl/certs

RUN useradd --shell /bin/bash debian && echo "debian ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
COPY infrastructure_key.pub /home/debian/.ssh/authorized_keys
RUN chown -R debian:debian /home/debian

# allow deb-systemd-invoke to start systemd services
RUN rm /usr/sbin/policy-rc.d
