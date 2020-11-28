FROM threefoldtech/phusion:20.04

ARG BRANCH
RUN apt-get update && apt-get install curl wget git python3-pip python3-venv redis-server tmux nginx restic -y

RUN pip3 install poetry
RUN mkdir -p /sandbox/code/github/threefoldtech

RUN git clone https://github.com/threefoldtech/js-sdk.git /sandbox/code/github/threefoldtech/js-sdk -b $BRANCH
WORKDIR /sandbox/code/github/threefoldtech/js-sdk
RUN poetry config virtualenvs.create false &&  poetry install
RUN poetry shell
RUN /etc/init.d/redis-server start
RUN python3 jumpscale/install/codeserver-install.py

RUN wget https://github.com/threefoldtech/zinit/releases/download/v0.1/zinit -O /sbin/zinit \
    && chmod +x /sbin/zinit

COPY rootfs /

ENTRYPOINT [ "zinit", "init" ]
