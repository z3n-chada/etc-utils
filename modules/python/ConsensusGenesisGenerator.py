"""
    Create a genesis.ssz for clients to digest given a config file.

    depends on eth2-testnet-genesis being located in your PATH; use the
    config docker as it is already set up.
"""
import os
import pathlib
import shutil
import subprocess

from ruamel import yaml


class ConsensusGenesisGenerator(object):
    def __init__(self, global_config, genesis_config_path):
        self.global_config = global_config
        self.genesis_config_path = genesis_config_path
        self.start_fork = global_config["pos-chain"]["config"]["genesis-fork-name"]
        self.preset_name = self.global_config["pos-chain"]["config"]["preset"]

        self.possible_forks = ["phase0", "altair", "merge", "sharding"]
        self.implemented_forks = ["phase0", "altair"]

        if not self.start_fork in self.possible_forks:
            raise Exception(
                f"Unknown fork name {state_fork} possible: ({self.possible_forks})"
            )
        if not self.start_fork in self.implemented_forks:
            raise Exception(
                f"fork {state_fork} not implemented.. currently implemented: ({self.implemented_forks})"
            )
        # path to write temporary files for eth2-testnet-genesis
        self.tmp_yaml = self.global_config["pos-chain"]["files"]["tmp-validator-config"]

        # lastly which forks came before.
        self.fork_presets = {
            "phase0": ["phase0"],
            "altair": ["phase0", "altair"],
            "merge": ["phase0", "altair", "merge"],
        }

        # how many pre-deployed validators.

    def _get_cmd(self, out_file):
        self._create_tmp_validator_yaml()

        cmd = [
            "eth2-testnet-genesis",
            self.start_fork,
            "--mnemonics",
            self.tmp_yaml,
            "--config",
            self.genesis_config_path,
            "--state-output",
            out_file,
        ]

        cmd += [args for args in self._preset_args()]

        # if tranches:
        #     self.cmd += ['--tranches-dir', '/tmp/tranches']

        return cmd

    def _preset_args(self):
        # all prior forks need a preset flag
        preset_args = []
        for fork in self.fork_presets[self.start_fork]:
            preset_args.append(f"--preset-{fork}")
            preset_args.append(self.preset_name)

        return preset_args

    def _create_tmp_validator_yaml(self):
        validator_data = self.global_config["pos-chain"]["accounts"]
        # eth2-testnet-genesis requires mnemonics to be in a yaml file.
        mnemonic = validator_data["validator-mnemonic"]
        if "num-predeployed-validators" in validator_data:
            count = validator_data["num-predeployed-validators"]
        else:
            # if not specified just generate them all.
            count = validator_data["total-validators"]

        with open(self.tmp_yaml, "w") as f:
            yaml.dump([{"mnemonic": mnemonic, "count": count}], f)

    def _delete_tmp_validator_yaml(self):
        os.remove(self.tmp_yaml)

    def clean_up(self):
        self._delete_tmp_validator_yaml()

    def write_to_file(self, out_file):
        print(self._get_cmd(out_file))
        subprocess.run(self._get_cmd(out_file))


def create_genesis_ssz(global_config, out_file, docker=True):
    if docker:
        genesis_config = global_config["pos-chain"]["files"]["docker-genesis-config"]
    else:
        genesis_config = global_config["pos-chain"]["files"]["host-genesis-config"]

    ccg = ConsensusGenesisGenerator(global_config, genesis_config)
    print(f"Writing genesis.ssz to {out_file}")
    ccg.write_to_file(out_file)
    ccg.clean_up()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="config", help="path to config to consume")
    parser.add_argument(
        "--out", dest="out", help="path to write the generated eth2-config.yaml"
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

    create_genesis_ssz(global_config, args.out, args.docker)
