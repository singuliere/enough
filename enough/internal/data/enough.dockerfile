ARG IMAGE_NAME
FROM ${IMAGE_NAME}

COPY dist/* .

RUN pip install *.tar.gz

CMD [ "--help" ]
ENTRYPOINT [ "python", "-m", "enough.internal.cmd" ]
