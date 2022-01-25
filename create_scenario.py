# Use this to create the scenario.
import argparse
import pathlib
import shutil
import time

import ruamel.yaml as yaml

from modules.python.ConsensusGenesisConfigWriter import create_consensus_config
from modules.python.ConsensusGenesisGenerator import create_genesis_ssz
from modules.python.DockerWriter import (
    create_bootstrap_docker_compose,
    create_docker_compose,
)
from modules.python.GethGenesisWriter import create_geth_genesis
from modules.python.TestnetDirectoryGenerator import create_testnet_dirs


def create_bootstrap_docker_compose_scenario(args):
    with open(args.config, "r") as f:
        global_config = yaml.safe_load(f.read())

    if args.docker:
        docker_compose_out = global_config["docker"]["docker-docker-compose-file"]
    else:
        docker_compose_out = global_config["docker"]["host-docker-compose-file"]

    create_bootstrap_docker_compose(
        global_config, docker_compose_out, args.config, args.docker, args.clean_last_run
    )


def clean_last_run(args):
    with open(args.config, "r") as f:
        global_config = yaml.safe_load(f.read())

    if args.docker:
        testnet_directory = pathlib.Path(
            global_config["pow-chain"]["files"]["docker-geth-data-dir"]
        ).parents[0]
    else:
        testnet_directory = pathlib.Path(
            global_config["pow-chain"]["files"]["host-geth-data-dir"]
        ).parents[0]

    if testnet_directory.exists():
        shutil.rmtree(str(testnet_directory))
    testnet_directory.mkdir()

    testnet_ready_file = testnet_directory.parents[0].joinpath("testnet-ready")

    if testnet_ready_file.exists():
        testnet_ready_file.unlink()


def create_scenario(args):
    with open(args.config, "r") as f:
        global_config = yaml.safe_load(f.read())

    if args.clean_last_run:
        clean_last_run(args)

    now = int(time.time())
    global_config["universal"]["now"] = now

    if args.docker:
        geth_genesis_out = global_config["pow-chain"]["files"][
            "docker-eth1-genesis-file"
        ]
        docker_compose_out = global_config["docker"]["docker-docker-compose-file"]
        consensus_config_out = global_config["pos-chain"]["files"][
            "docker-genesis-config"
        ]
        consensus_genesis_out = global_config["pos-chain"]["files"][
            "docker-genesis-ssz"
        ]
    else:
        geth_genesis_out = global_config["pow-chain"]["files"]["host-eth1-genesis-file"]
        docker_compose_out = global_config["docker"]["host-docker-compose-file"]
        consensus_config_out = global_config["pos-chain"]["files"][
            "host-genesis-config"
        ]
        consensus_genesis_out = global_config["pos-chain"]["files"]["host-genesis-ssz"]

    create_geth_genesis(global_config, geth_genesis_out)
    if not args.no_docker_compose:
        create_docker_compose(global_config, docker_compose_out, args.docker)
    create_consensus_config(global_config, consensus_config_out)
    create_genesis_ssz(global_config, consensus_genesis_out, args.docker)
    create_testnet_dirs(global_config, args.docker)
    # we are ready to go. unless we are running in self-contained go ahead and signal the dockers.
    if args.docker:
        signal_file = "/data/testnet-ready"
    else:
        signal_file = "shared-data/testnet-ready"

    with open(signal_file, "w") as f:
        f.write("1")


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
parser.add_argument(
    "--bootstrap-mode",
    dest="bootstrap_mode",
    action="store_true",
    help="Create a docker-compose that runs this script as the entry point",
)
parser.add_argument(
    "--no-docker-compose",
    dest="no_docker_compose",
    action="store_true",
    help="Skip outputting a docker-compose.yaml",
)

parser.add_argument(
    "--clean-last-run",
    dest="clean_last_run",
    action="store_true",
    help="remove old data directories before starting",
)

args = parser.parse_args()

if args.bootstrap_mode:
    create_bootstrap_docker_compose_scenario(args)
else:
    create_scenario(args)
