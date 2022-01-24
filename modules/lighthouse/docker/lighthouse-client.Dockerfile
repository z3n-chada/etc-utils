FROM rust:1.56.1-bullseye AS builder
WORKDIR /git
RUN apt-get update && apt-get -y upgrade && apt-get install -y cmake libclang-dev
RUN git clone https://github.com/sigp/lighthouse.git 
RUN cd lighthouse && make 

FROM ubuntu:latest
RUN apt-get update && apt-get -y upgrade && apt-get install -y --no-install-recommends \
  libssl-dev \
  ca-certificates \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/local/cargo/bin/lighthouse /usr/local/bin/lighthouse

ENTRYPOINT ["/bin/bash"]


