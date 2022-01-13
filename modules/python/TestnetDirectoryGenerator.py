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


class TestnetDirectoryGenerator(object):
    """
    depends on eth2-val-tools config docker ships with this already in
    its path.
    """

    def __init__(self, global_config, docker=True):
        self.global_config = global_config
        self.num_nodes = int(
            self.global_config["pos-chain"]["accounts"]["total-beacon-nodes"]
        )
        self.num_validators = int(
            self.global_config["pos-chain"]["accounts"]["total-validators"]
        )
        self.mnemonic = self.global_config["pos-chain"]["accounts"][
            "validator-mnemonic"
        ]
        if docker:
            self.genesis_ssz = self.global_config["pos-chain"]["files"][
                "docker-genesis-ssz"
            ]
            self.config = self.global_config["pos-chain"]["files"][
                "docker-genesis-config"
            ]
        else:
            self.genesis_ssz = self.global_config["pos-chain"]["files"][
                "host-genesis-ssz"
            ]
            self.config = self.global_config["pos-chain"]["files"][
                "host-genesis-config"
            ]

    def generate_all_validators(self, target_dir, password=None):
        # is password is none don't use.
        # python is a hassle with quoted args so use a str instead
        # of the typical list format
        cmd = (
            f"eth2-val-tools keystores --out-loc {target_dir} "
            + f"--source-min 0 --source-max {self.num_validators} "
            + f'--source-mnemonic "{self.mnemonic}"'
        )
        if password is not None:
            cmd += f' --prysm-pass "{password}"'
        subprocess.run(cmd, shell=True)

    def generate_piecewise_validators(self, target_dir, password=None):
        # similiar to all validators but breaks up the output into multiple folders
        if self.num_validators % self.num_nodes != 0:
            # TODO: don't be lazy.
            raise Exception("validators must evenly divide nodes!")
        divisor = int(self.num_validators / self.num_nodes)
        curr_offset = 0
        for x in range(divisor + 1):
            val_dir = f"node_{x}"
            cmd = (
                f"eth2-val-tools keystores --out-loc {target_dir}/{val_dir} "
                + f"--source-min 0 --source-max {self.num_validators} "
                + f'--source-mnemonic "{self.mnemonic}"'
            )
            if password is not None:
                cmd += f' --prysm-pass "{password}"'
            subprocess.run(cmd, shell=True)
            curr_offset += divisor


class PrysmTestnetDirectoryGenerator(TestnetDirectoryGenerator):
    """
    Prysm requires:
        piecewise validators with password
        config file
        genesis.ssz
    """

    def __init__(self, global_config, docker=True):
        super().__init__(global_config)
        if docker:
            self.testnet_dir = pathlib.Path(
                self.global_config["pos-chain"]["clients"]["prysm"][
                    "docker-testnet-dir"
                ]
            )
            self.password_file = self.global_config["pos-chain"]["clients"]["prysm"][
                "docker-wallet-path"
            ]
        else:
            self.testnet_dir = pathlib.Path(
                self.global_config["pos-chain"]["clients"]["prysm"]["host-testnet-dir"]
            )
            self.password_file = self.global_config["pos-chain"]["clients"]["prysm"][
                "host-wallet-path"
            ]
        self.validator_store_dir = pathlib.Path(str(self.testnet_dir) + "/validators/")
        self.password = self.global_config["pos-chain"]["clients"]["prysm"][
            "validator-password"
        ]
        self.testnet_dir.mkdir()

    def generate_testnet_dir(self):
        print("Creating prysm testnet directory...")
        # create local geneis ssz and config.yaml
        shutil.copy(src=self.genesis_ssz, dst=str(self.testnet_dir) + "/genesis.ssz"),
        shutil.copy(src=self.config, dst=str(self.testnet_dir) + "/config.yaml")
        # we also require a password file to run the prysm client without user input.
        with open(self.password_file, "w") as f:
            f.write(self.password)
        # all validators.
        self.generate_piecewise_validators(
            self.validator_store_dir, password=self.password
        )
        # create seperate node directories.
        divisor = int(self.num_validators / self.num_nodes)
        curr_offset = 0
        print("Organizing prysm testnet beacon node directories..")
        for x in range(divisor + 1):
            node_dir = pathlib.Path(str(self.testnet_dir) + f"/node_{x}")
            node_dir.mkdir()
            keystore_dir = pathlib.Path(
                str(self.testnet_dir) + f"/validators/node_{x}/"
            )
            for f in keystore_dir.glob("prysm/*"):
                if f.is_dir():
                    shutil.copytree(src=f, dst=f"{node_dir}/{f.name}")
                else:
                    shutil.copy(src=f, dst=f"{node_dir}/{f.name}")
        # done now clean up..
        shutil.rmtree(str(self.testnet_dir) + "/validators/")

def create_prysm_testnet_dirs(global_config, docker):
    pdg = PrysmTestnetDirectoryGenerator(global_config, docker=docker)
    pdg.generate_testnet_dir()


class LighthouseTestnetDirectoryGenerator(TestnetDirectoryGenerator):
    def __init__(self, global_config, docker=True):
        super().__init__(global_config)
        if docker:
            self.testnet_dir = pathlib.Path(
                self.global_config["pos-chain"]["clients"]["lighthouse"][
                    "docker-testnet-dir"
                ]
            )
        else:
            self.testnet_dir = pathlib.Path(
                self.global_config["pos-chain"]["clients"]["lighthouse"]["host-testnet-dir"]
            )
        self.validator_store_dir = pathlib.Path(str(self.testnet_dir) + "/validators/")
        self.testnet_dir.mkdir()

    def generate_testnet_dir(self):
        print("Creating lighthouse testnet directory...")
        # create local geneis ssz and config.yaml
        shutil.copy(src=self.genesis_ssz, dst=str(self.testnet_dir) + "/genesis.ssz"),
        shutil.copy(src=self.config, dst=str(self.testnet_dir) + "/config.yaml")
        self.generate_all_validators(self.validator_store_dir)
        # split up into subdirs.
        divisor = int(self.num_validators / self.num_nodes)
        curr_offset = 0
        print("Organizing lighthouse testnet beacon node directories..")
        # use secrets to get all the keys.
        all_key_paths = pathlib.Path(str(self.validator_store_dir) + "/secrets/").glob('*')
        sub_dir_keys = zip_longest(*[iter(all_key_paths)]*divisor)
        for ndx, keys in enumerate(sub_dir_keys):
            node_dir = pathlib.Path(str(self.testnet_dir) + f"/node_{ndx}/")
            node_dir.mkdir()
            secrets_dir = pathlib.Path(str(self.testnet_dir) + f"/node_{ndx}/secrets/")
            secrets_dir.mkdir()
            for k in keys:
                #validators then secrets
                src_key_dir = str(self.validator_store_dir)+f"/keys/{k.name}"
                dst_key_dir = str(node_dir) + f'/{k.name}'
                shutil.copytree(src_key_dir, dst_key_dir)
                dst_secret_key = str(secrets_dir)+f'/{k.name}'
                shutil.copy(k, dst_secret_key)
        shutil.rmtree(str(self.testnet_dir) + "/validators/")

def create_lighthouse_testnet_dirs(global_config, docker):
    lhdg = LighthouseTestnetDirectoryGenerator(global_config, docker=docker)
    lhdg.generate_testnet_dir()

def create_client_testnet_dir(global_config, client, docker):
    if client == 'prysm':
        create_prysm_testnet_dirs(global_config, docker)
    elif client == 'lighthouse':
        create_lighthouse_testnet_dirs(global_config, docker)
    else:
        raise Exception(f"Unimplented client label for testnet directory creation ({client})")

def create_testnet_dirs(global_config, docker):
    # tdg = TestnetDirectoryGenerator(global_config)
    # tdg.generate_validators(out_dir)
    pdg = PrysmTestnetDirectoryGenerator(global_config, docker=docker)
    pdg.generate_testnet_dir()


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
