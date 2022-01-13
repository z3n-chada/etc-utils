.PHONY: clean docker

base:
	mkdir -p shared-data/scripts
	mkdir -p shared-data/local_testnet/
	cp modules/geth/scripts/* shared-data/scripts/
	cp modules/bootnode/scripts/* shared-data/scripts/

docker:
	cd docker && ./build_docker.sh

client-dockers:
	cd modules/geth/docker && ./build_docker.sh
	cd modules/bootnode/docker && ./build_docker.sh

run-docker-config: base
	docker run -it -v $(shell pwd)/shared-data/:/data/ -v $(shell pwd):/source/ etc-builder:latest

clean:
	rm -r shared-data
	rm docker-compose.yaml
