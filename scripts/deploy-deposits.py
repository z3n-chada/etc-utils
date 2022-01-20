import json
import random
import subprocess

from ruamel import yaml
from web3.auto import w3

w3.eth.account.enable_unaudited_hdwallet_features()


def get_get_keypairs(global_config):
    k = {}
    mnemonic = global_config["pow-chain"]["accounts"]["eth1-account-mnemonic"]
    password = global_config["pow-chain"]["accounts"]["eth1-passphrase"]
    premines = global_config["pow-chain"]["accounts"]["eth1-premine"]
    for acc in premines:
        acct = w3.eth.account.from_mnemonic(
            mnemonic, account_path=acc, passphrase=password
        )
        k[acct.address] = acct.privateKey.hex()

    return k


def create_deposit_data(global_config, args):
    validator_mnemonic = global_config["pos-chain"]["accounts"]["validator-mnemonic"]
    withdrawl_mnemonic = global_config["pos-chain"]["accounts"]["withdrawl-mnemonic"]
    cmd = (
        f"eth2-val-tools deposit-data "
        + f"--source-min {args.start_offset} --source-max {args.start_offset + args.num_deposits} "
        + f"--fork-version {global_config['pos-chain']['config']['deposit']['chain-id']} "
        + f'--validators-mnemonic "{validator_mnemonic}" '
        + f'--withdrawals-mnemonic "{withdrawl_mnemonic}" '
        + f"--as-json-list "
    )

    x = subprocess.run(cmd, shell=True, capture_output=True)
    stdout_deposit_data = x.stdout

    return stdout_deposit_data


def deploy_deposit(args):
    with open(args.config, "r") as f:
        global_config = yaml.safe_load(f.read())

    deposit_data = create_deposit_data(global_config, args)
    key_pairs = get_get_keypairs(global_config)
    deposit_address = global_config["pow-chain"]["contracts"][
        "deposit-contract-address"
    ]

    # wrap ethereal with global_config.
    pubkey = random.choice(list(key_pairs.keys()))
    priv_key = key_pairs[pubkey]
    print(f"{pubkey} : {priv_key}")

    with open("/tmp/deposit_data", "wb") as f:
        f.write(deposit_data)

    send_ethereal_beacon_deposit(
        global_config,
        deposit_address,
        "/tmp/deposit_data",
        pubkey,
        priv_key,
        args.geth_ipc,
    )


def send_ethereal_beacon_deposit(
    global_config, deposit_address, data, pubkey, privkey, connection
):
    cmd = (
        f"/root/go/bin/ethereal beacon deposit "
        + f"--allow-unknown-contract=True "
        + f'--address="{deposit_address}" '
        + f'--data="/tmp/deposit_data" '
        + f'--from="{pubkey}" '
        + f'--privatekey="{privkey}" '
        + f'--connection="{connection}" '
        + "--debug "
        + "--wait"
    )

    print(subprocess.run(cmd, shell=True, capture_output=True))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="config", help="path to config to consume")
    parser.add_argument(
        "--geth-ipc",
        default="/data/local_testnet/geth/geth.ipc",
        dest="geth_ipc",
        help="path to the geth.ipc handle",
    )
    parser.add_argument(
        "--start-offset",
        dest="start_offset",
        default=80,
        help="min source to pass to generate deposit-data",
    )

    parser.add_argument(
        "--num-deposits",
        dest="num_deposits",
        default=20,
        help="min source to pass to generate deposit-data",
    )

    args = parser.parse_args()

    deploy_deposit(args)
