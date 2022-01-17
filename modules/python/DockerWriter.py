"""
    Modules to quickly write docker-compose.yaml files for use.

    These modules rely on yaml configurations that you pass in as an
    argument.
"""
from ruamel import yaml


class ClientWriter(object):
    """
    Generic client class to write services to docker-compose
    Just use this template and add your entrypoint in child class.
    """

    def __init__(self, global_config, client_config, name, curr_node):
        self.global_config = global_config
        self.client_config = client_config
        # used when we have multiple of the same client.
        self.curr_node = curr_node
        # constants.
        self.name = name
        self.image = self.client_config["image"]
        self.tag = self.client_config["tag"]
        self.network_name = self.global_config["docker"]["network-name"]
        self.volumes = [str(x) for x in self.global_config["docker"]["volumes"]]

    # inits for child classes.
    def config(self):
        return {
            "image": f"{self.image}:{self.tag}",
            "volumes": self.volumes,
            "networks": self._networking(),
        }

    def get_config(self):
        config = self.config()
        if self.client_config["debug"]:
            config["entrypoint"] = "/bin/bash"
            config["tty"] = True
            config["stdin_open"] = True
        else:
            config["entrypoint"] = self._entrypoint()
        return config

    def _networking(self):
        # first calculate the ip.
        return {self.network_name: {"ipv4_address": self.get_ip()}}

    def get_ip(self):
        prefix = ".".join(self.client_config["ip-start"].split(".")[:3]) + "."
        base = int(self.client_config["ip-start"].split(".")[-1])
        skip = self.curr_node * int(self.global_config["universal"]["ip-skip"])
        ip = prefix + str(base + skip)
        return ip

    def _entrypoint(self):
        raise Exception("over-ride this method")


class GethClientWriter(ClientWriter):
    def __init__(self, global_config, client_config, curr_node):
        super().__init__(
            global_config, client_config, f"geth-node-{curr_node}", curr_node
        )
        self.out = self.config()

    def _entrypoint(self):
        """
        ./launch-geth <datadir> <genesis.json> <network_id> <http port> <http apis> <ws_port> <ws_apis>
        """
        return [
            "/data/scripts/launch-geth.sh",
            str(self.global_config["pow-chain"]["files"]["docker-geth-data-dir"]),
            str(self.global_config["pow-chain"]["files"]["docker-eth1-genesis-file"]),
            str(self.client_config["network-id"]),
            str(self.client_config["http-port"]),
            str(self.client_config["http-apis"]),
            str(self.client_config["ws-port"]),
            str(self.client_config["ws-apis"]),
        ]


class PrysmClientWriter(ClientWriter):
    def __init__(self, global_config, client_config, curr_node):
        super().__init__(
            global_config, client_config, f"prysm-node-{curr_node}", curr_node
        )
        self.out = self.config()

    def _entrypoint(self):
        """
        ./launch-prysm <testnet-dir> <node-dir> <web3-provider> <deposit-contract> <ip-address> <tcp-port>
        TODO: bootnodes.
        """
        testnet_dir = str(self.client_config["docker-testnet-dir"])
        node_dir = f"{testnet_dir}/node_{self.curr_node}"
        geth_config = self.global_config["pow-chain"]["geth"]
        web3_provider = f'http://{geth_config["ip-start"]}:{geth_config["http-port"]}'
        deposit_contract = str(
            self.global_config["pow-chain"]["contracts"]["deposit-contract-address"]
        )
        return [
            "/data/scripts/launch-prysm.sh",
            testnet_dir,
            node_dir,
            web3_provider,
            deposit_contract,
            str(self.get_ip()),
            str(int(self.client_config["start-metric-port"]) + self.curr_node),
        ]


class LighthouseClientWriter(ClientWriter):
    def __init__(self, global_config, client_config, curr_node):
        super().__init__(
            global_config, client_config, f"lighthouse-node-{curr_node}", curr_node
        )
        self.out = self.config()

    def _entrypoint(self):
        """
        DEBUG_LEVEL TESTNET_DIR NODE_DIR P2P_PORT API_PORT
        IP_ADDR ETH1_ENDPOINT
        """
        testnet_dir = str(self.client_config["docker-testnet-dir"])
        node_dir = f"{testnet_dir}/node_{self.curr_node}"
        geth_config = self.global_config["pow-chain"]["geth"]
        web3_provider = f'http://{geth_config["ip-start"]}:{geth_config["http-port"]}'

        return [
            "/data/scripts/launch-lighthouse.sh",
            str(self.client_config["debug-level"]),
            testnet_dir,
            node_dir,
            str(self.client_config["start-p2p-port"] + self.curr_node),
            str(self.client_config["start-metric-port"] + self.curr_node),
            str(self.get_ip()),
            web3_provider,
        ]


class TekuClientWriter(ClientWriter):
    def __init__(self, global_config, client_config, curr_node):
        super().__init__(
            global_config, client_config, f"teku-node-{curr_node}", curr_node
        )
        self.out = self.config()

    def _entrypoint(self):
        """
        DEBUG_LEVEL=$1
        TESTNET_DIR=$2
        NODE_DIR=$3
        P2P_PORT=$4
        METRIC_PORT=$5
        REST_PORT=$6
        ETH1_ENDPOINT=$7
        """
        testnet_dir = str(self.client_config["docker-testnet-dir"])
        node_dir = f"{testnet_dir}/node_{self.curr_node}"
        geth_config = self.global_config["pow-chain"]["geth"]
        web3_provider = f'http://{geth_config["ip-start"]}:{geth_config["http-port"]}'
        return [
            "/data/scripts/launch-teku.sh",
            str(self.client_config["debug-level"]),
            testnet_dir,
            node_dir,
            str(self.client_config["start-p2p-port"] + self.curr_node),
            str(self.client_config["start-metric-port"] + self.curr_node),
            str(self.client_config["start-rest-port"] + self.curr_node),
            str(self.get_ip()),
            web3_provider,
        ]


class BootnodeClientWriter(ClientWriter):
    def __init__(self, global_config, client_config, curr_node):
        super().__init__(
            global_config, client_config, f"eth2-bootnode-{curr_node}", curr_node
        )
        self.out = self.config()

    def _entrypoint(self):
        """
        ./launch-bootnode <ip-address> <enr-port> <api-port> <private-key> <enr-path>
        launches a bootnode with a web port for fetching the enr, and
        fetches that enr and puts it in the local dir for other clients
        to find..
        """
        return [
            "/data/scripts/launch-eth2-bootnode.sh",
            str(self.get_ip()),
            str(self.client_config["enr-udp"]),
            str(self.client_config["api-port"]),
            str(self.client_config["private-key"]),
            str(self.client_config["bootnode-enr-file"]),
        ]


class DockerComposeWriter(object):
    """
    Class to create the actual docker-compose.yaml file.
    """

    def __init__(self, global_config):
        self.global_config = global_config
        self.yml = self._base()
        self.client_writers = {
            "prysm": PrysmClientWriter,
            "teku": TekuClientWriter,
            "lighthouse": LighthouseClientWriter,
        }

    def _base(self):
        return {
            "services": {},
            "networks": {
                self.global_config["docker"]["network-name"]: {
                    "driver": "bridge",
                    "ipam": {
                        "config": [
                            {"subnet": self.global_config["docker"]["ip-subnet"]}
                        ]
                    },
                }
            },
        }

    def add_services(self):
        """
        POW services + POS services.
        for now POW is geth.
        """
        curr_node = 0
        geth_config = self.global_config["pow-chain"]["geth"]
        for n in range(geth_config["num-nodes"]):
            gcw = GethClientWriter(self.global_config, geth_config, curr_node)
            self.yml["services"][gcw.name] = gcw.get_config()
            curr_node += 1

        bootnode_config = self.global_config["pos-chain"]["bootnodes"]["eth2-bootnode"]
        # note this does not contribute to curr_nodes
        for n in range(bootnode_config["num-nodes"]):
            bcw = BootnodeClientWriter(self.global_config, bootnode_config, n)
            self.yml["services"][bcw.name] = bcw.get_config()

        for services in self.global_config["pos-chain"]["clients"]:
            client_config = self.global_config["pos-chain"]["clients"][services]
            client = client_config["client-name"]
            for n in range(client_config["num-nodes"]):
                client_writer = self.client_writers[client](
                    self.global_config, client_config, n
                )
                self.yml["services"][client_writer.name] = client_writer.get_config()
                curr_node += 1

    def write_to_file(self, out_file):
        with open(out_file, "w") as f:
            yaml.dump(self.yml, f)


def create_docker_compose(global_config, out_file):
    dcw = DockerComposeWriter(global_config)
    dcw.add_services()
    dcw.write_to_file(out_file)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="config", help="path to config to consume")
    parser.add_argument(
        "--out", dest="out", help="path to write the generated docker-compose.yaml"
    )

    args = parser.parse_args()

    with open(args.config, "r") as f:
        global_config = yaml.safe_load(f.read())

    create_docker_compose(global_config, args.out)
