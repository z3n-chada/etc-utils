FROM ubuntu:18.04

ARG GIT_BRANCH="master"

# Update ubuntu
RUN apt-get update && \
	apt-get install -y --no-install-recommends \
		ca-certificates \
		software-properties-common \
		curl \
        wget \
		git \
		clang \
		vim
# Install golang
RUN add-apt-repository ppa:longsleep/golang-backports
RUN apt-get update && \
	apt-get install -y \
	golang

WORKDIR /git

RUN go get -d github.com/ethereum/go-ethereum && \
    cd /root/go/pkg/mod/github.com/ethereum/go-ethereum* && \
    go install ./...

RUN ln -s /root/go/bin/geth /usr/local/bin/geth

ENV GOPATH="/git"
# Install prysm
# (Hacky way to get specific version in GOPATH mode)
RUN mkdir -p /git/src/github.com/prysmaticlabs/
RUN cd /git/src/github.com/prysmaticlabs/ && \
    git clone --branch "$GIT_BRANCH" \
    --recurse-submodules \
    --depth 1 \
    https://github.com/prysmaticlabs/prysm

# Get dependencies
RUN cd /git/src/github.com/prysmaticlabs/prysm/ && \
    go get -t -d ./... && \
    go build ./... && \
    go install ./...

RUN ln -s /git/bin/beacon-chain /usr/local/bin/beacon-chain && \
    ln -s /git/bin/validator /usr/local/bin/validator

ENTRYPOINT ["/bin/bash"]
