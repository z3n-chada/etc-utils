# etc-utils
Ethereum testnet configuration utilities. Used for making quick docker based ethereum testnets.
# Initial setup:
1. make docker
2. make client-dockers

# How to run a scenario (testing-config.yaml in this example)
## Regular-mode
Generate the testnet data either on your host or from the etc-builder docker and deploy the docker-compose.yaml.

1. sudo make clean
2. make run-docker-config
3. (in docker) python3 /source/modules/python/create\_scenario.py --config /source/configs/testing-config.yaml --docker
4. (in docker) exit
5. (in project root directory on host) docker-compose up --force-recreate
## Bootstrap-mode
Bootstrap mode creates a docker-compose.yaml that contains a container that builds the testnet data for you.

1. rm -r shared-data/local\_testnet
2. mkdir shared-data/local\_testnet
3. rm shared-data/testnet-ready
4. docker-compose up --force-recreate
To set up the docker-compose.yaml in self-contained mode do the following:
1. sudo make clean
2. make run-docker-config
3. (in docker) python3 /source/modules/python/create\_scenario.py --config /source/configs/testing-config.yaml --docker --self-contained
4. (in docker) exit
5. (in project root directory on host) docker-compose up --force-recreate


# Configs
...

# Clients
Currently you can easily set up prysm, lighthouse, and teku beacon/validator combos. Additionally there is a status-checker

To enable this feature just set status-checker: enabled: True under scripts in the config file you are using. The code for this can be found
in the scripts/status\_checker.py

# Scripts
A generic client that just starts up a docker image with the entrypoint that you define. You must also specify the source of the script and its destination to be copied to. The source and be a list if you need multiple modules. 
# Modules
## Python
### DockerWriter.py
Creates docker-compose.yaml files to launch the testnet based on the config supplied.
### GethGenesisWriter.py
Create the geth genesis file with premines, contracts etc. 
### ConsensusGenesisConfigWriter.py
Create the consensus client config file.
