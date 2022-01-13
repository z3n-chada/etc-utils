# etc-utils
Ethereum testnet configuration utilities. Used for making quick docker based ethereum testnets.

Between runs use make clean; to build the scenario run the etc-scenario-builder docker, then to run the scenario simply use docker-compose.

# Initial setup:
1. make docker
2. make client-dockers

# How to run a scenario (testing-config.yaml in this example)
1. sudo make clean
2. make run-docker-config
3. (in docker) python3 /source/modules/python/create\_scenario.py --config /source/configs/testing-config.yaml --docker
4. (in docker) exit
5. (in project root directory on host) docker-compose up --force-recreate


# Modules
## Python
### DockerWriter.py
Creates docker-compose.yaml files to launch the testnet based on the config supplied.
### GethGenesisWriter.py
Create the geth genesis file with premines, contracts etc. 
### ConsensusGenesisConfigWriter.py
Create the consensus client config file.
