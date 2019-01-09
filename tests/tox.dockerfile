RUN pip install tox
RUN apt-get install -y git
RUN git init
COPY requirements-dev.txt tox.ini setup.cfg setup.py README.md /opt/
RUN tox --notest
COPY . /opt
