FROM threefoldtech/phusion:19.10

RUN apt-get update && apt-get install wget git python3-pip python3-venv redis-server tmux nginx restic -y
RUN pip3 install poetry
RUN mkdir -p /sandbox/code/github/threefoldtech
RUN git clone https://github.com/threefoldtech/js-sdk.git /sandbox/code/github/threefoldtech/js-sdk -b development
WORKDIR /sandbox/code/github/threefoldtech/js-sdk
RUN poetry config virtualenvs.create false && poetry install
RUN poetry shell
RUN /etc/init.d/redis-server start
RUN python3 jumpscale/install/codeserver-install.py

COPY rootfs /
ADD zinit /sbin/zinit

ENTRYPOINT [ "zinit", "init" ]
