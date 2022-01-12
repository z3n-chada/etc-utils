FROM ubuntu:20.04

ENV TZ=America
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# Update ubuntu
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        software-properties-common \
        curl \
        wget \
        git \
        build-essential \
        binutils-dev \
        cmake \
        gpg-agent \
        gcc-9-plugin-dev \
        python3-dev \
        libpcre3-dev \
        netcat \
        net-tools \
        python3-pip \
        jq \
        vim

# Install golang
RUN add-apt-repository ppa:longsleep/golang-backports
RUN apt-get update && \
	apt-get install -y \
	golang

RUN pip3 install ruamel.yaml

WORKDIR /git

RUN go get -d github.com/ethereum/go-ethereum && \
    cd /root/go/pkg/mod/github.com/ethereum/go-ethereum* && \
    go install ./...

RUN ln -s /root/go/bin/geth /usr/local/bin/geth

