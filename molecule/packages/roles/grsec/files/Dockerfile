# ubuntu:14.04 as of 2017-12-15
FROM ubuntu@sha256:084989eb923bd86dbf7e706d464cf3587274a826b484f75b69468c19f8ae354c

RUN apt-get update && apt-get install -y bc build-essential fakeroot gcc-4.8 gcc-4.8-plugin-dev kernel-package libncurses5-dev libssl-dev make python-requests
CMD ["bash", "-c", "if ! make -j4 deb-pkg >& out ; then cat out ; exit 1 ; fi"]
