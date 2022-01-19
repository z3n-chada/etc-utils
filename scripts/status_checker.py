import copy
import random
import time

import requests
from ruamel import yaml


class ConsensusStatusChecker(object):
    def __init__(self, global_config, start_slot=32):
        self.start_slot = start_slot
        self.global_config = global_config
        self.clients = {}
        self._get_client_info_from_config()

        # apis to access for status
        self.queryPaths = [
            "/eth/v1/beacon/headers",
            "/eth/v1/beacon/pool/attestations",
            "/eth/v1/beacon/pool/attester_slashings",
            "/eth/v1/beacon/pool/proposer_slashings",
            "/eth/v1/beacon/pool/voluntary_exits",
            "/eth/v1/debug/beacon/heads",
            "/eth/v1/node/syncing",
        ]
        self.states = ["head", "justified", "finalized"]
        self.statePaths = [
            "committees",
            "validator_balances",
            "root",
            "fork",
            "finality_checkpoints",
        ]
        self.headQueryPaths = ["/eth/v1/beacon/states/"]
        self.slotQueryPaths = ["/eth/v1/beacon/blocks/"]

    def fetch_head_slot(self, client, http=True):
        if http == False:
            raise Exception("Not implemented")
        print(self.clients)
        print(client)
        port = self.clients[client]["rest"]
        response = requests.get(f"http://{client}:{port}/eth/v1/node/syncing")
        print(response.json())
        return response.json()["data"]["head_slot"]

    def wait_for_genesis(self, client_addr=None, retries=10, retry_delay=15, http=True):
        if http == False:
            raise Exception("Not implemented")
        if client_addr is None:
            # just choose on.
            ip, ports = random.choice(list(self.clients.items()))
        print(f"{ip} -> {ports}")
        response = self._get_with_retry(
            f"http://{ip}:{ports['rest']}/eth/v1/beacon/genesis",
            retries=retries,
            retry_delay=retry_delay,
        )
        if response is None or response.status_code != 200:
            raise Exception("Timeout for genesis wait exceeded expectation")
        print(f"Genesis detected from {ports['client']}:{ip}:{ports['rest']}")
        genesis_time = int(response.json()["data"]["genesis_time"])
        curr_time = int(time.time())
        while curr_time < genesis_time:
            print(
                f"Waiting for genesis {genesis_time - curr_time} seconds remaining.",
                flush=True,
            )
            time.sleep(1)
            curr_time = int(time.time())

        print(response.content)

    def wait_for_slot(self, oracle, target_slot, http=True):
        if http == False:
            raise Exception("Not implemented")
        curr_slot = 0
        while curr_slot < target_slot:
            ports = self.clients[oracle]
            response = requests.get(
                f"http://{oracle}:{ports['rest']}/eth/v1/node/syncing"
            )
            curr_slot = int(response.json()["data"]["head_slot"])
            print(f"waiting for slot... {curr_slot}/{target_slot}", flush=True)
            time.sleep(10)

    def _fetch_response(self, client_ip, path, http=True):
        if http == False:
            raise Exception("Not implemented")
        ports = self.clients[client_ip]
        req = f"http://{client_ip}:{ports['rest']}{path}"
        response = requests.get(req)
        return response

    def compare_responses(self, oracle, query):
        oracle_response = self._fetch_response(oracle, query)
        clients = copy.deepcopy(self.clients)
        clients.pop(oracle)
        for client in clients:
            response = self._fetch_response(client, query)
            print(response.content)

            if response.content != oracle_response.content:
                print(f"FAILED! \n{oracle_response.content}\n{response.content}\n")

    def monitor_network_health(self, total_passes=3):
        clients = copy.deepcopy(self.clients)
        oracle = random.choice(list(clients.keys()))
        clients.pop(oracle)

        self.wait_for_slot(oracle, self.start_slot)

        curr_pass = 0
        while curr_pass != total_passes:

            head_slot = self.fetch_head_slot(oracle)

            for query in self.queryPaths:
                self.compare_responses(oracle, query)
                time.sleep(0.5)

            for slot_query in self.slotQueryPaths:
                query = f"{slot_query}{head_slot}"
                self.compare_responses(oracle, query)
                time.sleep(0.5)

            for state_path in self.statePaths:
                for state in self.states:
                    query = f"/eth/v1/beacon/states/{state}/{state_path}"
                    self.compare_responses(oracle, query)
                time.sleep(0.5)
            time.sleep(10)
            print("Finished monitor pass {curr_pass}/{total_passes}")
            curr_pass += 1

    def _get_client_info_from_config(self):
        for service in self.global_config["pos-chain"]["clients"]:
            client_config = self.global_config["pos-chain"]["clients"][service]
            client = client_config["client-name"]
            for ndx in range(client_config["num-nodes"]):
                prefix = ".".join(client_config["ip-start"].split(".")[:3]) + "."
                base = int(client_config["ip-start"].split(".")[-1])
                ip = prefix + str(base + ndx)
                self.clients[ip] = {
                    "client": client_config["client-name"],
                    "p2p": client_config["start-p2p-port"] + ndx,
                    "rest": client_config["start-rest-port"] + ndx,
                    "http": client_config["start-http-port"] + ndx,
                }

    def _get_with_retry(
        self, url, desired_response_code=200, timeout=5, retries=30, retry_delay=15
    ):
        print(f"Attempting {url}")
        attempt = 1
        last_response = None
        while attempt <= retries:
            status_code = 500
            try:
                last_response = requests.get(url, timeout=timeout)
                status_code = last_response.status_code
                print(f"status_code={status_code}; response={last_response.json()}")
            except:
                pass
            if status_code != desired_response_code:
                print(f"\tattempt={attempt}/{retries}; delay={retry_delay}s")
                time.sleep(retry_delay)
                attempt += 1
            else:
                break
        return last_response


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="config", help="path to config to consume")

    args = parser.parse_args()

    with open(args.config, "r") as f:
        global_config = yaml.safe_load(f.read())

    csc = ConsensusStatusChecker(global_config)
    csc.wait_for_genesis()
    csc.monitor_network_health()
