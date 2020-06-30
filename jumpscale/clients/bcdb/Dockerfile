FROM threefoldtech/js-ng:latest
RUN apt-get update &&\
    apt-get install musl-tools -y
RUN git clone https://github.com/threefoldtech/0-db.git /sandbox/code/github/threefoldtech/0-db
RUN git clone https://github.com/threefoldtech/bcdb.git /sandbox/code/github/threefoldtech/bcdb
WORKDIR /sandbox/code/github/threefoldtech/0-db
RUN make
RUN cp bin/zdb /usr/local/bin/ 

WORKDIR /sandbox/code/github/threefoldtech/bcdb
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs -o /tmp/rustup.sh
RUN bash /tmp/rustup.sh --profile default -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN make
RUN cp target/x86_64-unknown-linux-musl/release/bcdb /usr/local/bin
RUN pip3 install grpcio protobuf requests-unixsocket
WORKDIR /sandbox/code/github/threefoldtech/js-sdk
ENTRYPOINT ["/sbin/my_init"]
