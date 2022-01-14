import json

from ruamel import yaml
from web3.auto import w3

w3.eth.account.enable_unaudited_hdwallet_features()

"""
    generate keyfiles for geth genesis..
"""

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="config", help="path to config to consume")

    args = parser.parse_args()

    with open(args.config, "r") as f:
        config = yaml.safe_load(f.read())

    mnemonic = config["pow-chain"]["accounts"]["eth1-account-mnemonic"]
    password = config["pow-chain"]["accounts"]["eth1-passphrase"]
    premines = config["pow-chain"]["accounts"]["eth1-premine"]
    for acc in premines:
        acct = w3.eth.account.from_mnemonic(
            mnemonic, account_path=acc, passphrase=password
        )
        print(f"address: {acct.address}")
        print(f"private: {acct.privateKey.hex()}")
        keyfile = acct.encrypt(password)
        with open(f"keyfile-{acct.address}.key", "w") as f:
            json.dump(keyfile, f)
