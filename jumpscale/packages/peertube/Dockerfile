FROM ubuntu:bionic

# Avoid tzdata interactive dialog
ENV DEBIAN_FRONTEND=noninteractive

# Install PeerTube's dependencies.
# Packages are from https://github.com/Chocobozzz/PeerTube#dependencies
RUN apt-get update &&\
    apt-get install -y curl ffmpeg g++ git gnupg make nano openssl postgresql postgresql-contrib redis-server &&\
    curl -sL https://deb.nodesource.com/setup_10.x | bash - &&\
    curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - &&\
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list &&\
    apt-get update &&\
    apt-get install -y nodejs yarn &&\
    rm -rf /var/lib/apt/lists/*

# Download PeerTube's source code.
RUN git clone -b release/2.3.0 https://github.com/Chocobozzz/PeerTube /home/user/PeerTube
WORKDIR /home/user/PeerTube

# Install Node.js dependencies and setup PostgreSQL
RUN ls
RUN  yarn install  &&\
     service postgresql start &&\
     su postgres -c "psql --file=/home/user/PeerTube/support/docker/dev/setup_postgres.sql" &&\
     npm run build -- --light

# Expose PeerTube sources as a volume
VOLUME /home/user/PeerTube

# Expose API and frontend
EXPOSE 3000 9000

# Start PostgreSQL and Redis
RUN apt-get update &&\
    apt-get install -y openssh-server

# Copy startup script
COPY startup.sh /usr/local/bin/
COPY default.yaml config/default.yaml
RUN chmod +x /usr/local/bin/startup.sh
CMD /usr/local/bin/startup.sh

# CMD service postgresql start; sleep 3; service postgresql start; redis-server --daemonize yes; NODE_OPTIONS="--max-old-space-size=4096" npm run dev
