FROM rust:1.56.1-bullseye AS builder
WORKDIR /git
RUN apt-get update && apt-get -y upgrade && apt-get install -y cmake libclang-dev
RUN git clone https://github.com/sigp/lighthouse.git 
RUN cd lighthouse && make 

FROM ubuntu:latest
ENV TZ=America
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update && apt-get -y upgrade && apt-get install -y --no-install-recommends \
  libssl-dev \
		ca-certificates \
		software-properties-common \
		curl \
        wget \
		git \
		clang \
        python3-dev \
        python3-pip \
		vim 

RUN add-apt-repository ppa:longsleep/golang-backports
RUN apt-get update && \
	apt-get install -y \
	golang \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /git

RUN pip3 install web3 ruamel.yaml

RUN go get -d github.com/ethereum/go-ethereum && \
    cd /root/go/pkg/mod/github.com/ethereum/go-ethereum* && \
    go install ./...

RUN ln -s /root/go/bin/geth /usr/local/bin/geth

COPY --from=builder /usr/local/cargo/bin/lighthouse /usr/local/bin/lighthouse

ENTRYPOINT ["/bin/bash"]


