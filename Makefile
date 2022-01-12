.PHONY: clean docker

docker:
	cd docker && ./build_docker.sh

run-docker-config:
	docker run -it -v $(shell pwd):/data/ etc-builder:latest

clean:
	rm docker-compose.yaml
