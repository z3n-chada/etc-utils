# Use this to create the scenario.
import argparse
import shutil
import time

import ruamel.yaml as yaml

from DockerWriter import create_docker_compose
from GethGenesisWriter import create_geth_genesis
from ConsensusGenesisConfigWriter import create_consensus_config
from ConsensusGenesisGenerator import create_genesis_ssz
from TestnetDirectoryGenerator import create_testnet_dirs


def create_scenario(args):
    with open(args.config, "r") as f:
        global_config = yaml.safe_load(f.read())

    now = int(time.time())
    global_config["universal"]["now"] = now

    if args.docker:
        geth_genesis_out = global_config['pow-chain']['files']['docker-eth1-genesis-file']
        docker_compose_out = global_config['docker']['docker-docker-compose-file']
        consensus_config_out = global_config['pos-chain']['files']['docker-genesis-config']
        consensus_genesis_out = global_config['pos-chain']['files']['docker-genesis-ssz']
    else:
        geth_genesis_out = global_config['pow-chain']['files']['host-eth1-genesis-file']
        docker_compose_out = global_config['docker']['host-docker-compose-file']
        consensus_config_out = global_config['pos-chain']['files']['host-genesis-config']
        consensus_genesis_out = global_config['pos-chain']['files']['host-genesis-ssz']

    create_geth_genesis(global_config, geth_genesis_out)
    create_docker_compose(global_config, docker_compose_out)
    create_consensus_config(global_config, consensus_config_out)
    create_genesis_ssz(global_config, consensus_genesis_out, args.docker)
    create_testnet_dirs(global_config, args.docker)


parser = argparse.ArgumentParser()
parser.add_argument(
    "--config", dest="config", required=True, help="path to config to consume"
)
parser.add_argument(
    "--docker",
    dest="docker",
    action="store_true",
    help="(suggested) if you are using the supplied docker to create the environment",
)

args = parser.parse_args()
create_scenario(args)
