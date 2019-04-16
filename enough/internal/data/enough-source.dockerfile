ARG IMAGE_NAME
FROM ${IMAGE_NAME}

COPY requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt

COPY dist/* .
RUN pip3 install *.tar.gz

RUN python -m enough.internal.cmd install api/data/enough.service > /etc/systemd/system/enough.service && systemctl enable enough

CMD [ "help" ]
ENTRYPOINT [ "python", "-m", "enough.internal.cmd" ]
