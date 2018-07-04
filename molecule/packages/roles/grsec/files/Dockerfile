FROM ubuntu:xenial

RUN apt-get update && apt-get install -y bc build-essential fakeroot g++-5 gcc-5 gcc-5-plugin-dev kernel-package libncurses5-dev libssl-dev make python-requests
CMD ["bash", "-c", "if ! make -j4 deb-pkg >& out ; then cat out ; exit 1 ; fi"]
