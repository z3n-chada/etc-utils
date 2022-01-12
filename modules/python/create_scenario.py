# Use this to create the scenario.
import argparse
import shutil
import time

import ruamel.yaml as yaml

from DockerWriter import create_docker_compose
from GethGenesisWriter import create_geth_genesis


def create_scenario(args):
    with open(args.config, "r") as f:
        global_config = yaml.safe_load(f.read())

    now = int(time.time())
    global_config["universal"]["now"] = now

    create_geth_genesis(
        global_config, global_config["pow-chain"]["files"]["eth1-genesis-file"]
    )
    if args.docker:
        create_docker_compose(global_config, "/source/docker-compose.yaml")
    else:
        create_docker_compose(global_config, 'docker-compose.yaml')


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
