ARG BASE_IMAGE
FROM ${BASE_IMAGE}
USER root
COPY lock.mjs acquire-lock.py install.py patch.py verify.py filelock-4.2.1-py3-none-any.whl /opt/zedbiz/wiki-lock/
RUN python3 -I -B /opt/zedbiz/wiki-lock/install.py && \
    python3 -I -B /opt/zedbiz/wiki-lock/patch.py && \
    python3 -I -B /opt/zedbiz/wiki-lock/verify.py --record && \
    python3 -I -B /opt/zedbiz/wiki-lock/verify.py && \
    rm /opt/zedbiz/wiki-lock/filelock-4.2.1-py3-none-any.whl && \
    rm -f /opt/zedbiz/wiki-lock/hold-lock.py
LABEL com.zedbiz.wiki-lock="filelock-fd-v2" com.zedbiz.filelock-version="4.2.1"
USER node
