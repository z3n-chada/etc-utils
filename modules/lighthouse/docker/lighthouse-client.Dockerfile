FROM rust:1.53.0 AS builder
RUN apt-get update && apt-get -y upgrade && apt-get install -y cmake
RUN git clone --recurse-submodules https://github.com/sigp/lighthouse.git
RUN cd lighthouse && make install install-lcli

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
        vim

WORKDIR /git


COPY --from=builder /usr/local/cargo/bin/lcli /usr/local/bin/lcli
COPY --from=builder /usr/local/cargo/bin/lighthouse /usr/local/bin/lighthouse

ENTRYPOINT ["/bin/bash"]


