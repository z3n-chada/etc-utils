from ruamel import yaml


class ConsensusConfigWriter(object):
    def __init__(self, global_config):
        cc = global_config["pos-chain"]["config"]  # consensus config
        preset = str(cc["preset"])
        print(preset)
        pc = global_config["universal"]["consensus-presets"][preset]  # preset config
        self.yml = f"""
PRESET_BASE: {cc['preset']}

# Genesis
# ---------------------------------------------------------------
# [customized]
MIN_GENESIS_ACTIVE_VALIDATOR_COUNT: {pc['min-genesis-active-validator-count']}

MIN_GENESIS_TIME: {global_config['universal']['now']}
GENESIS_FORK_VERSION: 0x{cc['genesis-fork-version']:08x}
GENESIS_DELAY: {cc['genesis-delay']}

# Forking
# ---------------------------------------------------------------
# Values provided for illustrative purposes.
# Individual tests/testnets may set different values.

# Altair
ALTAIR_FORK_VERSION: 0x{cc['forks']['altair-fork-version']:08x}
ALTAIR_FORK_EPOCH: {cc['forks']['altair-fork-epoch']}
# Merge
# MERGE_FORK_VERSION: 0x{cc['forks']['merge-fork-version']:08x}
# MERGE_FORK_EPOCH: {cc['forks']['merge-fork-epoch']}
# Bellatrix (aka merge)
BELLATRIX_FORK_VERSION: 0x{cc['forks']['merge-fork-version']:08x}
BELLATRIX_FORK_EPOCH: {cc['forks']['merge-fork-epoch']}
# Sharding
SHARDING_FORK_VERSION: 0x{cc['forks']['sharding-fork-version']:08x}
SHARDING_FORK_EPOCH: {cc['forks']['sharding-fork-epoch']}

# TBD, 2**32 is a placeholder. Merge transition approach is in active R&D.
MIN_ANCHOR_POW_BLOCK_DIFFICULTY: 4294967296

# Time parameters
# ---------------------------------------------------------------
# [customized] Faster for testing purposes
SECONDS_PER_SLOT: {pc['seconds-per-slot']}
# 14 (estimate from Eth1 mainnet)
SECONDS_PER_ETH1_BLOCK: {global_config['pow-chain']['seconds-per-eth1-block']}
MIN_VALIDATOR_WITHDRAWABILITY_DELAY: 256
SHARD_COMMITTEE_PERIOD: {pc['shard-committee-period']}
ETH1_FOLLOW_DISTANCE: {pc['eth1-follow-distance']}

# Validator cycle
# ---------------------------------------------------------------
# 2**2 (= 4)
INACTIVITY_SCORE_BIAS: 4
# 2**4 (= 16)
INACTIVITY_SCORE_RECOVERY_RATE: 16
# 2**4 * 10**9 (= 16,000,000,000) Gwei
EJECTION_BALANCE: 16000000000
# 2**2 (= 4)
MIN_PER_EPOCH_CHURN_LIMIT: 4
# [customized] scale queue churn at much lower validator counts for testing
CHURN_LIMIT_QUOTIENT: {pc['churn-limit-quotient']}

# Transition
# ---------------------------------------------------------------
# TBD, 2**256-2**10 is a placeholder
TERMINAL_TOTAL_DIFFICULTY: 5000000000
# By default, don't use these params
TERMINAL_BLOCK_HASH: 0x0000000000000000000000000000000000000000000000000000000000000000
TERMINAL_BLOCK_HASH_ACTIVATION_EPOCH: 18446744073709551615


# Deposit contract
# ---------------------------------------------------------------
# Execution layer chain
DEPOSIT_CHAIN_ID: {cc['deposit']['chain-id']}
DEPOSIT_NETWORK_ID: {cc['deposit']['network-id']}
# Allocated in Execution-layer genesis
DEPOSIT_CONTRACT_ADDRESS: {cc['deposit']['contract-address']}
"""

    def write_to_file(self, out_file):
        with open(out_file, "w") as f:
            f.write(self.yml)


def create_consensus_config(global_config, out_file):
    ccw = ConsensusConfigWriter(global_config)
    ccw.write_to_file(out_file)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="config", help="path to config to consume")
    parser.add_argument(
        "--out", dest="out", help="path to write the generated eth2-config.yaml"
    )

    args = parser.parse_args()

    with open(args.config, "r") as f:
        global_config = yaml.safe_load(f.read())

    create_consensus_config(global_config, args.out)
