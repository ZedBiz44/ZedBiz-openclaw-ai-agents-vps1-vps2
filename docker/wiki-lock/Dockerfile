ARG BASE_IMAGE
FROM ${BASE_IMAGE}
USER root
COPY hold-lock.py lock.mjs patch.py verify.py /opt/zedbiz/wiki-lock/
RUN test -x /usr/bin/python3 && python3 -c 'import fcntl' && python3 /opt/zedbiz/wiki-lock/patch.py /app && python3 /opt/zedbiz/wiki-lock/verify.py
LABEL com.zedbiz.wiki-lock="flock-v1"
USER node
