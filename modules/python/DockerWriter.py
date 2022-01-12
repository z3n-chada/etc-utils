"""
    Modules to quickly write docker-compose.yaml files for use.

    These modules rely on yaml configurations that you pass in as an
    argument.
"""
from ruamel import yaml


class DockerComposeWriter(object):
    """
    Class to create the actual docker-compose.yaml file.
    """

    def __init__(self, global_config):
        self.global_config = global_config
        self.yml = self._base()

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

    def write_to_file(self, out_file):
        with open(out_file, "w") as f:
            yaml.dump(self.yml, f)


def create_docker_compose(global_config, out_file):
    dcw = DockerComposeWriter(global_config)
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
