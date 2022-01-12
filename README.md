# etc-utils
Ethereum testnet configuration utilities. Used for making quick docker based ethereum testnets.

Between runs use make clean; to build the scenario run the etc-scenario-builder docker, then to run the scenario simply use docker-compose.

# Modules
## Python
### DockerWriter.py
Creates docker-compose.yaml files to launch the testnet based on the config supplied.

