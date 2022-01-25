.PHONY: clean docker

base:
	mkdir -p shared-data/scripts
	mkdir -p shared-data/local_testnet/
	mkdir -p shared-data/geth-keystores/
	cp modules/geth/scripts/* shared-data/scripts/
	cp modules/bootnode/scripts/* shared-data/scripts/
	cp modules/geth/data/* shared-data/geth-keystores/
	cp modules/prysm/scripts/* shared-data/scripts/
	cp modules/lighthouse/scripts/* shared-data/scripts/
	cp modules/teku/scripts/* shared-data/scripts/
	cp scripts/* shared-data/scripts/

client-dockers:
	cd modules/geth/docker && ./build_docker.sh
	cd modules/bootnode/docker && ./build_docker.sh
	cd modules/prysm/docker && ./build_docker.sh
	cd modules/lighthouse/docker && ./build_docker.sh
	cd modules/teku/docker && ./build_docker.sh

docker:
	cd docker && ./build_docker.sh

run-docker-config: base
	docker run -it -v $(shell pwd)/shared-data/:/data/ -v $(shell pwd):/source/ etc-builder:latest

clean:
	rm -r shared-data
	rm docker-compose.yaml
