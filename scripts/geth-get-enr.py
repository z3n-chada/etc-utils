import json

import web3
from ruamel import yaml

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="config", help="path to config to consume")
    parser.add_argument(
        "--docker",
        dest="docker",
        action="store_true",
        help="are we running in docker? (changes the default paths)",
    )

    args = parser.parse_args()

    with open(args.config, "r") as f:
        global_config = yaml.safe_load(f.read())

    if args.docker:
        geth_ipc = (
            global_config["pow-chain"]["files"]["docker-geth-data-dir"] + "geth.ipc"
        )
    else:
        geth_ipc = (
            global_config["pow-chain"]["files"]["host-geth-data-dir"] + "geth.ipc"
        )
    web3_provider = web3.IPCProvider(geth_ipc)
    w3 = web3.Web3(web3_provider)

    admin_info = w3.geth.admin.node_info()

    print(admin_info["enode"], end=" ")
