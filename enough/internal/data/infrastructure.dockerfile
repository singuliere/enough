ARG IMAGE_NAME
FROM ${IMAGE_NAME}

RUN apt-get install -y sudo
RUN useradd --shell /bin/bash debian && echo "debian ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
COPY infrastructure_key.pub /home/debian/.ssh/authorized_keys
RUN chown -R debian:debian /home/debian/.ssh/authorized_keys
