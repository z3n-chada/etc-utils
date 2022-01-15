FROM ubuntu:18.04

WORKDIR /git
RUN apt-get update && apt-get install -y git openjdk-11-jdk curl vim

RUN git clone https://github.com/Consensys/teku.git && \
    cd /git/teku && \
    ./gradlew distTar installDist

RUN ln -s /git/teku/build/install/teku/bin/teku /usr/local/bin/teku

ENTRYPOINT ["/bin/bash"]
