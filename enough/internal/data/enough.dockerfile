ARG ENOUGH_VERSION
ARG PIP3_OPTS

RUN pip3 install ${PIP3_OPTS} enough==${ENOUGH_VERSION} # install the package and all dependencies
RUN pip3 install --no-cache-dir --force-reinstall --no-deps ${PIP3_OPTS} enough==${ENOUGH_VERSION} # replace this comment with timestamp to force reinstallation of the packages even if the version does not change

RUN python -m enough.internal.cmd --domain enough.community install api/data/enough.service > /etc/systemd/system/enough.service && systemctl enable enough
RUN python -m enough.internal.cmd --domain enough.community install api/data/bootstrap.service > /etc/systemd/system/bootstrap.service && systemctl enable bootstrap
RUN python -m enough.internal.cmd --domain enough.community install api/data/bootstrap.sh > /usr/local/bin/bootstrap.sh && chmod +x /usr/local/bin/bootstrap.sh

ENTRYPOINT [ "python", "-m", "enough.internal.cmd" ]
