FROM python:3.7

WORKDIR /usr/src/app
ADD . .
RUN python setup.py install

ENTRYPOINT [ "/usr/local/bin/python", "-m", "gcp_hashicorp_packer_reaper.server"]
