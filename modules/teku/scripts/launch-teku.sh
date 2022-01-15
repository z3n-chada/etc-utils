#!/bin/bash

# Usage: <LOGGING> <TESTNET_DIR> <NODE_DIR> <P2P_PORT> <METRIC_PORT> <REST_PORT> <ETH1_ENDPOINT>

DEBUG_LEVEL=$1 
TESTNET_DIR=$2
NODE_DIR=$3
P2P_PORT=$4
METRIC_PORT=$5
REST_PORT=$6
IP_ADDR=$7
ETH1_ENDPOINT=$8

sleep 10 # wait for bootnode to come up

bootnode_enr=`cat $TESTNET_DIR/../bootnode/enr.dat`
echo $bootnode_enr
# beacon node
teku --network "$TESTNET_DIR/config.yaml" \
    --data-path "$NODE_DIR" \
    --p2p-enabled=true \
    --logging="$DEBUG_LEVEL" \
    --initial-state "$TESTNET_DIR/genesis.ssz" \
    --eth1-endpoint "$ETH1_ENDPOINT" \
    --p2p-discovery-bootnodes="$bootnode_enr" \
    --metrics-enabled=true \
    --metrics-interface=0.0.0.0 \
    --metrics-port="$METRIC_PORT" \
    --metrics-host-allowlist="*" \
    --p2p-discovery-enabled=true \
    --p2p-advertised-ip="$IP_ADDR" \
    --p2p-peer-lower-bound=1 \
    --p2p-port="$P2P_PORT" \
    --p2p-advertised-port="$P2P_PORT" \
    --p2p-advertised-udp-port="$P2P_PORT" \
    --rest-api-enabled=true \
    --rest-api-docs-enabled=true \
    --rest-api-interface=0.0.0.0 \
    --rest-api-port="$REST_PORT" \
    --rest-api-host-allowlist="*" \
    --metrics-host-allowlist="*" \
    --metrics-host-allowlist="*" \
    --metrics-host-allowlist="*" &

sleep 15

teku vc \
    --network "$TESTNET_DIR/config.yaml" \
    --data-path "$NODE_DIR" \
    --beacon-node-api-endpoint "http://localhost:$REST_PORT" \
    --validators-graffiti="hello" \
    --validator-keys "$NODE_DIR/keys:$NODE_DIR/secrets"
