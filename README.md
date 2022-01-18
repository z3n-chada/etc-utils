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
