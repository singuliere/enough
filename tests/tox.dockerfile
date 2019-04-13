RUN pip install tox
RUN git init
COPY requirements-dev.txt tox.ini setup.cfg setup.py README.md /opt/
RUN tox --notest
COPY . /opt
RUN cd /opt && git add . && git config user.email "you@example.com" && git config user.name "Your Name" && git commit -a -m 'for tests'
