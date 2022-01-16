"""
    Create per-client testnet directories.

    Clients expect slightly different inputs for starting up, we take care
    of them here.
"""
import os
import pathlib
import shutil
import subprocess
from itertools import zip_longest

from ruamel import yaml


class TestnetDirectoryManager(object):
    def __init__(self, global_config, docker=True):
        self.docker = docker
        self.global_config = global_config
        self.total_nodes = int(
            self.global_config["pos-chain"]["accounts"]["total-beacon-nodes"]
        )
        self.total_validators = int(
            self.global_config["pos-chain"]["accounts"]["total-validators"]
        )

        self.mnemonic = self.global_config["pos-chain"]["accounts"][
            "validator-mnemonic"
        ]

        self.client_generators = {"prysm": PrysmTestnetGenerator}

        self.generated_validators = {}

    # used to generate the
    def _generate_validator_stores(
        self, start, num_nodes, num_validators, out_dir, password=None, metadata="None"
    ):
        divisor = int(num_validators / num_nodes)
        if num_validators % num_nodes != 0:
            raise Exception("Validators must evenly divide nodes")

        curr_offset = start
        for x in range(num_nodes):
            val_dir = f"node_{x}"
            cmd = (
                f"eth2-val-tools keystores --out-loc {out_dir}/{val_dir} "
                + f"--source-min {curr_offset} --source-max {curr_offset + divisor} "
                + f'--source-mnemonic "{self.mnemonic}"'
            )
            if password is not None:
                cmd += f' --prysm-pass "{password}"'
            subprocess.run(cmd, shell=True)
            curr_offset += divisor

        if (
            start in self.generated_validators
            or curr_offset in self.generated_validators
        ):
            raise Exception(f"Got overlapping validator keys from mnemonic {mnemonic}")

        for x in range(start, curr_offset):
            self.generated_validators[x] = metadata

    def generate_all_client_testnet_dirs(self):
        for service in self.global_config["pos-chain"]["clients"]:
            client_config = self.global_config["pos-chain"]["clients"][service]
            client = client_config["client-name"]

            cg = self.client_generators[client](
                self.global_config, client_config, self.docker
            )
            self._generate_validator_stores(*cg.get_validator_info())
            cg.finalize_testnet_dir()


class TestnetDirectoryGenerator(object):
    """
    Responsible for moving and editing files required to the clients to
    work. Validators keys are generated through the manager so we can
    check for overlaps across clients.
    """

    def __init__(self, global_config, client_config, docker=True):
        self.global_config = global_config
        self.client_config = client_config

        if docker:
            self.genesis_ssz = self.global_config["pos-chain"]["files"][
                "docker-genesis-ssz"
            ]
            self.config = self.global_config["pos-chain"]["files"][
                "docker-genesis-config"
            ]
            self.testnet_dir = pathlib.Path(self.client_config["docker-testnet-dir"])
        else:
            self.genesis_ssz = self.global_config["pos-chain"]["files"][
                "host-genesis-ssz"
            ]
            self.config = self.global_config["pos-chain"]["files"][
                "host-genesis-config"
            ]
            self.testnet_dir = pathlib.Path(self.client_config["host-testnet-dir"])

        self.testnet_dir.mkdir()
        shutil.copy(src=self.genesis_ssz, dst=str(self.testnet_dir) + "/genesis.ssz"),
        shutil.copy(src=self.config, dst=str(self.testnet_dir) + "/config.yaml")


class PrysmTestnetGenerator(TestnetDirectoryGenerator):
    def __init__(self, global_config, client_config, docker):
        super().__init__(global_config, client_config, docker)
        # prysm only stuff.
        if docker:
            self.password_file = self.client_config["docker-wallet-path"]
        else:
            self.password_file = self.client_config["host-wallet-path"]

        self.password = self.client_config["validator-password"]

        with open(self.password_file, "w") as f:
            f.write(self.password)

    def get_validator_info(self):
        # return data neccessary.
        return (
            self.client_config["validator-offset-start"],
            self.client_config["num-nodes"],
            self.client_config["num-validators"],
            pathlib.Path(str(self.testnet_dir) + "/validators"),
            self.password,
            "prysm-client",
        )

    def finalize_testnet_dir(self):
        """
        Copy validator info into local client.
        """
        print(f"Finalizing prysm client {self.testnet_dir} testnet directory.")
        for ndx in range(self.client_config["num-nodes"]):
            node_dir = pathlib.Path(str(self.testnet_dir) + f"/node_{ndx}")
            node_dir.mkdir()
            keystore_dir = pathlib.Path(
                str(self.testnet_dir) + f"/validators/node_{ndx}/"
            )
            for f in keystore_dir.glob("prysm/*"):
                if f.is_dir():
                    shutil.copytree(src=f, dst=f"{node_dir}/{f.name}")
                else:
                    shutil.copy(src=f, dst=f"{node_dir}/{f.name}")
        # done now clean up..
        shutil.rmtree(str(self.testnet_dir) + "/validators/")


def create_testnet_dirs(global_config, docker):
    tdm = TestnetDirectoryManager(global_config, docker)
    tdm.generate_all_client_testnet_dirs()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="config", help="path to config to consume")
    parser.add_argument(
        "--out", dest="out", help="path to write the generated testnet directory."
    )
    parser.add_argument(
        "--docker",
        dest="docker",
        action="store_true",
        help="are we in a docker environment.",
    )

    args = parser.parse_args()

    with open(args.config, "r") as f:
        global_config = yaml.safe_load(f.read())

    create_testnet_dirs(global_config, args.docker)
